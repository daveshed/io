# IO
Concrete implementation of the gpio interface required by the `stage` controller package. The aim here is to invert the dependency on `RPi.GPIO` (or any other gpio library) that `stage` may depend on. At run time, the actual gpio implementation will be injected.
