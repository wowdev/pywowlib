# python-mpq
[![Build Status](https://api.travis-ci.org/HearthSim/python-mpq.svg?branch=master)](https://travis-ci.org/HearthSim/python-mpq)

Python bindings for Ladislav Zezula's [StormLib](http://zezula.net/en/mpq/stormlib.html).


## Usage

### Reading MPQs

```py
import mpq
f = mpq.MPQFile("base-Win.MPQ")

if "example.txt" in mpq:
	print(mpq.open("example.txt").read())
```

### Patching MPQs

Modern MPQs support archive patching. The filename usually contains the
`from` and `to` build numbers.

```py
f.patch("hs-6024-6141-Win-final.MPQ")
```

### Writing MPQs

Writing MPQs is not supported.


## License

This project is licensed under the terms of the MIT license.
The full license text is available in the LICENSE file.
