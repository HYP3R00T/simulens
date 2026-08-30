from typing import Annotated

from pydantic import Field

ColorChannel = Annotated[float, Field(ge=0.0, le=1.0)]
Color = tuple[ColorChannel, ColorChannel, ColorChannel, ColorChannel]
Point2D = tuple[float, float]
