## covid-scraper


*Maestro* is a program that collects news information from the *Agencia
lupa* and *g1* websites related to fake news about COVID-19. Then, creates a
json file with all of its data (array of objects), witch includes:

```
 [
    {
        "title"        : string,
        "description"  : string,
        "imgageURL"    : string,
        "newsURL"      : string,
        "date"         : string,
        "time"         : string,
        "author"       : string,
        "source"       : string
    },
]
```

`date` is `d/m/a` and time is 24h format.

