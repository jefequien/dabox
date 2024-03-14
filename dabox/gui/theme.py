"""Viser GUI theme"""

import viser
from viser.theme import TitlebarButton, TitlebarConfig, TitlebarImage


def setup_viser_theme(server: viser.ViserServer) -> None:
    """Layout GUI interface."""
    buttons = (
        TitlebarButton(
            text="Github",
            icon="GitHub",
            href="https://github.com/jefequien/dabox",
        ),
        TitlebarButton(
            text="Documentation",
            icon="Description",
            href="https://github.com/jefequien/dabox",
        ),
    )
    image = TitlebarImage(
        image_url_light="https://github.com/jefequien/dabox/blob/main/docs/dabox-logo.png?raw=true",
        image_url_dark="https://github.com/jefequien/dabox/blob/main/docs/dabox-logo-dark.png?raw=true",
        image_alt="DABOX Logo",
        href="https://github.com/jefequien/dabox",
    )
    titlebar_theme = TitlebarConfig(buttons=buttons, image=image)

    # Configure theme
    dark_mode = server.add_gui_checkbox("Dark mode", initial_value=True)

    def configure_theme() -> None:
        server.configure_theme(
            titlebar_content=titlebar_theme,
            control_layout="collapsible",
            control_width="medium",
            dark_mode=dark_mode.value,
            show_logo=True,
            show_share_button=False,
            brand_color=(230, 180, 30),
        )

    dark_mode.on_update(lambda _: configure_theme())
    configure_theme()
