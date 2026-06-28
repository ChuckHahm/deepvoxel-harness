import click
from loguru import logger

from deepvoxel.application.runner import run_engagement


@click.command()
@click.option("--engagement", default=None, help="Engagement slug to run")
@click.option("--replay", is_flag=True, default=False, help="Run example engagement replay")
def main(engagement: str, replay: bool):
    if replay:
        logger.info("Running engagement replay...")
        run_engagement("example")
    elif engagement:
        run_engagement(engagement)
    else:
        logger.error("Provide --engagement <slug> or --replay")


if __name__ == "__main__":
    main()
