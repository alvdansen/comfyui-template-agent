"""Media category keyword mapping for node classification."""

CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "video": [
        "video", "animation", "animate", "frame", "motion", "film",
        "mp4", "gif", "interpolat", "optical flow", "wan", "hunyuan-video",
        "mochi", "ltx", "svd", "i2v", "t2v", "v2v",
    ],
    "image": [
        "image", "photo", "picture", "upscale", "denoise", "inpaint",
        "outpaint", "flux", "sdxl", "stable diffusion", "controlnet",
        "img2img", "txt2img", "lora",
    ],
    "audio": [
        "audio", "sound", "music", "voice", "speech", "tts",
        "whisper", "bark", "elevenlabs",
    ],
    "3d": [
        "3d", "mesh", "point cloud", "depth", "normal map",
        "hunyuan3d", "stable3d", "triposr",
    ],
}


def classify_node(name: str, description: str, category: str = "") -> list[str]:
    """Return matching media categories for a node.

    Concatenates name, description, and category, then checks against keyword lists.
    Returns matching categories or ["utility"] if none match.
    """
    text = f"{name} {description} {category}".lower()
    matches = []
    for cat, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            matches.append(cat)
    return matches or ["utility"]
