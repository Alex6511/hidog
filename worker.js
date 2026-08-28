const params = new URLSearchParams(self.location.search)
const scriptName = params.get("script") || "./hidog.js"

try {
  const hidogModule = await import(scriptName)
  const wasmName = scriptName.replace(".js", "_bg.wasm")

  await hidogModule.default(wasmName)
} catch (e) {
  console.error("worker failed to initialize:", e)
  throw e
}
