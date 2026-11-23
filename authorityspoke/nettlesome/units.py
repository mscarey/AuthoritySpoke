from sympy.physics.units import (
    Quantity,
    gram,
    grams,
    hectare,
    hour,
    hours,
    kilogram,
    kilograms,
    meter,
    meters,
    mile,
    miles,
    second,
    seconds,
    yard,
    yards,
)
from sympy.physics.units import convert_to as sympy_convert_to

acre = acres = Quantity("acre")
acre.set_global_relative_scale_factor(0.4047, hectare)
