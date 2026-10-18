#!/usr/bin/env swift
import Foundation
import AppKit
import Vision

let paths = Array(CommandLine.arguments.dropFirst())
if paths.isEmpty {
  fputs("Usage: swift analyze_positions.swift image1.png [image2.png ...]\n", stderr)
  exit(64)
}

let expected = [
  "THE SILENT ATLAS": "TITLE",
  "THE WAYFINDER CHRONICLES": "SERIES",
  "NORTH STAR PRESS": "PUBLISHER"
]

func normalized(_ value: String) -> String {
  return value.uppercased().filter { $0.isLetter || $0.isNumber }
}

print("FILE\tROLE\tOCR_TEXT\tLEFT_%\tTOP_%\tRIGHT_%\tBOTTOM_%\tCENTER_X_%\tCENTER_Y_%")
for path in paths {
  let url = URL(fileURLWithPath: path)
  guard FileManager.default.fileExists(atPath: url.path) else {
    fputs("Skipping missing file: \(path)\n", stderr)
    continue
  }
  do {
    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.usesLanguageCorrection = false
    request.recognitionLanguages = ["en-US"]
    request.customWords = ["THE SILENT ATLAS", "THE WAYFINDER CHRONICLES", "NORTH STAR PRESS"]
    request.minimumTextHeight = 0.004
    let handler = VNImageRequestHandler(url: url, options: [:])
    try handler.perform([request])
    let observations = (request.results ?? []).sorted {
      let aTop = 1.0 - $0.boundingBox.maxY
      let bTop = 1.0 - $1.boundingBox.maxY
      if abs(aTop - bTop) > 0.015 { return aTop < bTop }
      return $0.boundingBox.minX < $1.boundingBox.minX
    }
    for observation in observations {
      guard let text = observation.topCandidates(1).first?.string else { continue }
      let textN = normalized(text)
      var role = "OTHER"
      for (target, targetRole) in expected {
        if textN.contains(normalized(target)) || normalized(target).contains(textN) {
          role = targetRole
          break
        }
      }
      let box = observation.boundingBox // Vision uses normalized coordinates, origin at bottom-left.
      let left = box.minX * 100.0
      let right = box.maxX * 100.0
      let top = (1.0 - box.maxY) * 100.0
      let bottom = (1.0 - box.minY) * 100.0
      let cx = (box.minX + box.maxX) * 50.0
      let cy = (1.0 - (box.minY + box.maxY) / 2.0) * 100.0
      let cleanText = text.replacingOccurrences(of: "\t", with: " ").replacingOccurrences(of: "\n", with: " ")
      print("\(url.lastPathComponent)\t\(role)\t\(cleanText)\t\(String(format: "%.1f", left))\t\(String(format: "%.1f", top))\t\(String(format: "%.1f", right))\t\(String(format: "%.1f", bottom))\t\(String(format: "%.1f", cx))\t\(String(format: "%.1f", cy))")
    }
    if observations.isEmpty {
      print("\(url.lastPathComponent)\tNO_TEXT_DETECTED\t(no OCR results)\t-\t-\t-\t-\t-\t-")
    }
  } catch {
    fputs("OCR failed for \(path): \(error)\n", stderr)
  }
}
