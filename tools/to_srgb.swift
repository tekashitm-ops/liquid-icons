// Convierte los PNG que exporta ictool (Display P3, 16 bits) a sRGB de 8 bits, en su sitio.
//
// Stream Deck no aplica perfiles de color: lee los valores tal cual, como si fueran sRGB.
// Sin esta conversión la tecla mostraría los colores aprobados apagados (un P3 leído como sRGB).
// La conversión la hace ColorSync (CoreGraphics) al dibujar la imagen en un lienzo sRGB.
//
// Uso:  swift tools/to_srgb.swift renders/*.png
import CoreGraphics
import Foundation
import ImageIO
import UniformTypeIdentifiers

func fail(_ message: String) -> Never {
    FileHandle.standardError.write(Data("error: \(message)\n".utf8))
    exit(1)
}

let srgb = CGColorSpace(name: CGColorSpace.sRGB)!
let paths = CommandLine.arguments.dropFirst()
if paths.isEmpty { fail("no se indicó ningún PNG") }

for path in paths {
    let url = URL(fileURLWithPath: path)
    guard let source = CGImageSourceCreateWithURL(url as CFURL, nil),
          let image = CGImageSourceCreateImageAtIndex(source, 0, nil) else { fail("no se pudo leer \(path)") }
    let from = image.colorSpace?.name as String? ?? "sin perfil"

    let (w, h) = (image.width, image.height)
    guard let ctx = CGContext(data: nil, width: w, height: h, bitsPerComponent: 8, bytesPerRow: 0,
                              space: srgb, bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue)
    else { fail("no se pudo crear el lienzo sRGB para \(path)") }
    ctx.interpolationQuality = .none
    ctx.draw(image, in: CGRect(x: 0, y: 0, width: w, height: h))
    guard let converted = ctx.makeImage() else { fail("no se pudo convertir \(path)") }

    // Se escribe a un archivo temporal y luego se sustituye el original
    let tmp = url.deletingLastPathComponent().appendingPathComponent(".\(url.lastPathComponent).srgb")
    guard let dest = CGImageDestinationCreateWithURL(tmp as CFURL, UTType.png.identifier as CFString, 1, nil)
    else { fail("no se pudo escribir \(tmp.path)") }
    CGImageDestinationAddImage(dest, converted, nil)
    if !CGImageDestinationFinalize(dest) { fail("no se pudo guardar \(tmp.path)") }
    _ = try? FileManager.default.removeItem(at: url)
    do { try FileManager.default.moveItem(at: tmp, to: url) } catch { fail("no se pudo sustituir \(path): \(error)") }

    print("sRGB 8 bits: \(url.lastPathComponent) \(w)x\(h) (antes: \(from), \(image.bitsPerComponent) bits)")
}
