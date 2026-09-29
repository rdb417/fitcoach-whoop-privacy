# BDE.VC shot library: AI video prompts

For Veo (Gemini app, Flow or the Gemini API), Kling or Runway. ChatGPT itself
cannot generate video.

Settings: 16:9, 1080p, 8 seconds, sound off (the reel has its own sound
design). Keep the subject centred so the same clip also crops to 9:16 and to
the 4:5 inset window. Generate 2 to 4 takes of each and keep the best.

Add this style line to the end of every prompt:

> Cinematic and photorealistic, anamorphic lens, 24fps, dark moody lighting with deep black shadows and warm golden highlights, subtle film grain, slow deliberate camera movement, subject centred in frame. No text, no logos, no brand names, no flags, no mission patches, no readable markings, no human faces.

Negative prompt, if the tool has a field for it:

> text, captions, subtitles, watermark, logo, brand name, flag, insignia, mission patch, letters, numbers, faces, cartoon, CGI look, oversaturated, bright daylight

## Space

**1. Rocket liftoff (hero).** An unbranded white orbital rocket lifts off from a coastal launch pad at dusk. The camera tilts up to follow it as a huge exhaust plume and rolling clouds of steam glow orange beneath it, sparks and debris scattering across the pad.

**2. Engine ignition.** Near darkness, then an unbranded rocket engine on a test stand ignites: a bright orange-white plume erupts horizontally from a dark engine bell, violent heat shimmer, shock diamonds, lit smoke billowing, slight camera shake.

**3. Empty pad at dusk.** A wide locked-off shot of an empty coastal launch pad, a lone steel tower silhouetted against a deep orange horizon fading to dark blue, a few red warning lights, faint haze. Completely still.

**4. Orbital docking.** Two unbranded white spacecraft modules approach each other in low Earth orbit with the curve of the Earth below, a slow deliberate approach until the docking rings make soft contact and latches engage, golden sunlight glinting on the hulls.

## Quantum

**5. Quantum computer cooling down.** A slow orbit around a gold-plated dilution refrigerator hanging in a dark lab, tiers of gold plates and coiled copper cables. In the foreground a cryogen dewar vents white vapour that drifts slowly across the frame, frost forming on a steel fitting, warm rim light, shallow depth of field.

**6. Qubit chip macro.** An extreme close-up slow push-in on a superconducting quantum processor chip, fine gold wire bonds and microwave lines catching warm light, mounted in a copper sample holder, tiny specks of frost, very shallow depth of field.

*Accuracy note: a real fridge cools down over days inside a sealed vacuum can, with nothing visible. The vapour from the dewar stands in for "cold". Fine for a hype reel, but a physicist will know.*

## Energy

**7. Battery beside an electric vehicle.** A slow dolly past an exposed high-performance battery pack on a dark studio floor, rows of cylindrical cells with a warm line of light sweeping across them. Behind it, the sleek unbadged chassis of an electric sports car sits in soft focus.

**8. Cell production line.** Robotic arms place cylindrical battery cells into a module on a dark production line, precise rhythmic motion, warm overhead light glinting on the metal, shallow depth of field.

**9. Geothermal drilling.** A slow push-in on a geothermal drill bit boring into dark rock, dust and heat haze rising, a faint orange glow at the bore, warm industrial light.

## Physical AI

**10. Humanoid robots, warehouse.** Two unbranded matte-graphite humanoid robots working in a dim warehouse, one lifting a crate onto a high shelf and the other carrying a box down the aisle, smooth deliberate motion, warm rim light. Helmet-like heads with no faces.

**11. Humanoid robot, factory assembly.** An unbranded matte-graphite humanoid robot at a workbench fitting a metal component into an assembly with precise hand movements, sparks from a distant welding cell in the background, warm light. Helmet-like head, no face.

**12. Humanoid robot walking.** An unbranded humanoid robot walks toward the camera down a long dark industrial hall, strong backlight creating a rim-lit silhouette, haze in the air, slow steady steps.

## Industry

**13. Forging press.** A hydraulic press slams down onto a red-hot steel billet, a burst of sparks spraying outward, the glowing metal squashing under the impact, dark forge with orange light.

**14. Glowing ingot.** A macro shot of a single red-hot metal ingot resting on a black surface in total darkness, intense orange and yellow glow, heat shimmer rising above it, slow push-in.

## Checking every take (before it goes anywhere near the edit)

- Scrub frame by frame for any text, logo, flag, patch or badge. Generators often invent fake lettering.
- Reject look-alikes of real products: a Falcon 9 or Starship, the IBM System One, Tesla Optimus, Figure, Boston Dynamics Atlas, any recognisable car.
- No human faces, including on robots.
- Log the tool, model, prompt, generation ID and date in `../licenses/LICENSES.md`.
