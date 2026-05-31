from sympy.physics.units import (
    gram,
    grams,
    hectare,
    hour,
    hours,
    kilogram,
    kilograms,
    mile,
    miles,
    meter,
    meters,
    second,
    seconds,
    yard,
    yards,
)
from sympy.physics.units import convert_to as sympy_convert_to
from sympy.physics.units import Quantity

acre = acres = Quantity("acre")
acre.set_global_relative_scale_factor(0.4047, hectare)
