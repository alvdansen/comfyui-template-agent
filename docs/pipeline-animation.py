"""
Manim animation: ComfyUI Template Agent skill pipeline flow.
Renders the discover → audit → validate → compose → document flow.

Usage (requires Manim installed):
    manim render -pql docs/pipeline-animation.py PipelineFlow

Stretch goal for Phase 14 — not a milestone blocker.
"""

from manim import *


class PipelineFlow(Scene):
    """Animates the 5-step skill pipeline from discovery to documentation."""

    # Color palette matching the architecture diagram
    PURPLE = "#7C3AED"
    BLUE = "#2563EB"
    GREEN = "#16A34A"
    LIGHT_PURPLE = "#F3E8FF"
    LIGHT_BLUE = "#DBEAFE"
    LIGHT_GREEN = "#DCFCE7"

    def construct(self):
        # Title
        title = Text("ComfyUI Template Agent", font_size=36, color=WHITE)
        subtitle = Text("Skill Pipeline", font_size=24, color=self.PURPLE)
        subtitle.next_to(title, DOWN, buff=0.3)
        self.play(Write(title), run_time=1)
        self.play(FadeIn(subtitle), run_time=0.5)
        self.wait(1)
        self.play(FadeOut(title), FadeOut(subtitle))

        # Pipeline steps
        steps = [
            ("Discover", "/comfy-discover", "Find trending nodes"),
            ("Audit", "/comfy-template-audit", "Check coverage gaps"),
            ("Validate", "/comfy-validate", "12 guideline checks"),
            ("Compose", "/comfy-compose", "Build workflow JSON"),
            ("Document", "/comfy-document", "Generate submissions"),
        ]

        boxes = []
        arrows = []
        x_start = -5.5
        x_step = 2.8

        for i, (name, cmd, desc) in enumerate(steps):
            x = x_start + i * x_step

            # Box
            box = RoundedRectangle(
                width=2.4, height=1.6, corner_radius=0.15,
                fill_color=self.LIGHT_PURPLE, fill_opacity=0.3,
                stroke_color=self.PURPLE, stroke_width=2,
            ).move_to([x, 0, 0])

            # Step number
            num = Text(str(i + 1), font_size=14, color=self.PURPLE)
            num.move_to([x - 0.9, 0.55, 0])

            # Name
            label = Text(name, font_size=20, color=WHITE, weight=BOLD)
            label.move_to([x, 0.2, 0])

            # Command
            command = Text(cmd, font_size=11, color=self.PURPLE)
            command.move_to([x, -0.15, 0])

            # Description
            description = Text(desc, font_size=12, color=GRAY_B)
            description.move_to([x, -0.5, 0])

            group = VGroup(box, num, label, command, description)
            boxes.append(group)

            # Arrow to next step
            if i < len(steps) - 1:
                arrow = Arrow(
                    start=[x + 1.2, 0, 0],
                    end=[x + x_step - 1.2, 0, 0],
                    color=self.PURPLE,
                    stroke_width=2,
                    tip_length=0.2,
                )
                arrows.append(arrow)

        # Animate: boxes appear one by one with arrows
        for i, box in enumerate(boxes):
            self.play(FadeIn(box, shift=UP * 0.3), run_time=0.6)
            if i < len(arrows):
                self.play(GrowArrow(arrows[i]), run_time=0.4)

        self.wait(1)

        # Flow animation: highlight moves through pipeline
        highlight = RoundedRectangle(
            width=2.6, height=1.8, corner_radius=0.15,
            stroke_color=self.GREEN, stroke_width=3,
            fill_opacity=0,
        )

        for i, box in enumerate(boxes):
            target_pos = box[0].get_center()
            if i == 0:
                highlight.move_to(target_pos)
                self.play(Create(highlight), run_time=0.3)
            else:
                self.play(highlight.animate.move_to(target_pos), run_time=0.5)
            self.wait(0.3)

        # Final output
        self.play(FadeOut(highlight))

        output_text = Text(
            "submission-ready template",
            font_size=24, color=self.GREEN, weight=BOLD,
        )
        output_text.next_to(boxes[-1], DOWN, buff=0.8)

        output_arrow = Arrow(
            start=boxes[-1][0].get_bottom(),
            end=output_text.get_top(),
            color=self.GREEN,
            stroke_width=2,
        )

        self.play(GrowArrow(output_arrow), Write(output_text), run_time=0.8)
        self.wait(2)

        # Fade everything out
        all_elements = VGroup(*boxes, *arrows, output_text, output_arrow)
        self.play(FadeOut(all_elements), run_time=1)
