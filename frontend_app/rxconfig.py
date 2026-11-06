import reflex as rx

config = rx.Config(
    app_name="frontend_app",
    default_color_mode="light",
    plugins=[
        rx.plugins.RadixThemesPlugin(
            theme=rx.theme(
                appearance="light",
                accent_color="blue",
                gray_color="slate",
                radius="large",
                has_background=True,
            )
        ),
    ],
    disable_plugins=[
        rx.plugins.SitemapPlugin,
    ],
)
