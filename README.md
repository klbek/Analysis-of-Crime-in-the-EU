# Kriminalita v zemích EU

## Cíl projektu

Cílem projektu je automatizace zpracování dat o kriminalitě v zemích EU a jejich statistická analýza. Projekt se zaměřuje na identifikaci extrémů v kriminalitních činech v jednotlivých státech a sledování jejich dlouhodobých trendů. Projekt poskytne podklad pro zodpovězení klíčových otázek, jako například: Které země EU čelí největším výkyvům v kriminalitě? Jaké trestné činy jsou nejvíce na vzestupu?

## Dataset z Eurostatu

Pro práci s datasetem je potřeba si nastudovat příslušné [dokumentace](https://ec.europa.eu/eurostat/cache/metadata/en/crim_sims.htm) a [doporučení](https://ec.europa.eu/eurostat/documents/3859598/18846431/KS-GQ-24-010-EN-N.pdf/ef737587-085e-6018-8038-e41f59222020?version=3.0&t=1712826948630) od Eurostatu, abychom se vyvarovali špatnému používání dat a ve výsledku i chybné interpretaci.

Zpracován je základní dataset 'Police-recorded offences by offence category (crim_off_cat)' z kategorie 'Police-recorded offences(crim_off)' z [databáze Crime and criminal justice](https://ec.europa.eu/eurostat/web/crime/database) z Eurostatu.

Číselníky pro rozkódování kriminálních činnů a rozkódování zemí byly vytvořeny za pomoci Pythonu, raw data byla ručně zkopírovaná po rozkliknutí tabulek základního datasetu v menu (nepodařilo se najít žádný jiný a lepší zdroj) do textového souboru a dále vyčištěna. Číselníky jsou uloženy jako .csv ve složce [data](/data).

Významné změny mezi roky musí být potvrzeny zeměmi, dříve Eurostat data nezveřejní. Pro práci s daty je toto zásadní údaj, protože můžeme předpokládat, že extrémní výkyvy jsou opravdu výkyvy, ne chyba při zveřejňování dat. 

Některé zločiny jsou v jedné zemi považovány za přestupky, v jiné za trestné činy.

Nejvhodnější je srovnávat trendy, nikoli absolutní úrovně kriminality. Vzhledem k jiné legislativě, metodice sběru dat (i když je standardizovaná), není vhodné porovnávat státy mezi sebou. Případně je potřeba si velmi podrobně nastudovat dokumentaci a pro jednotlivé kriminální činy si zjistit, které státy bychom mohli teoreticky srovnávat. 

V datech figurují i podkategorie, které v datech ponecháváme a v případě potřeby je na závěr odfiltrujeme:

- Sexual violence: Rape, Sexual assault
- Sexual exploitation: Child pornography
- Burglary: Burglary of private residential premises
- Theft: Theft of a motorized vehicle or parts thereof
- Corruption: Bribery

Od roku 2019 včetně přestali data postytovat Scotland, England and Wales, Northern Ireland. 


## Metodika a postup zpracování dat

Data se ukázala jako velmi bohatá na informace avšak ve své původní podobě špatně interpretovatelná, bylo potřeba je transformovat. Protože se brzy ukázalo, že je kód díky tolika manipulacím a různým statistický výpočtům špatně čitelný, znovupožitelný aj, ke zpracování dat se přistoupilo jinak. Celý základní dataset je uzavřen do třídy `EurostatCrimeTable` a refenerčně se odkazuje na třídu `Statistics`, která za nás automatizovaně vypočítá podstatné údaje a obslouží výjimky. Pomocí funkce `create_summary_df_1all()` třídy `EurostatCrimeTable` nám vznikne nový souhrnný dataframe, ze kterého můžeme i bez grafů číst zajímavé informace. 

V rámci transformace je potřeba data nahrát, rozdělit první složený sloupec na jednotlivé sloupce, rozkódovat číselné kody trestných činnů a názvy zemí, nechat si pouze údaje, které jsou přepočítané na 100tis obyvatel dané země. Na závěr je potřeba data unpivotovat a jednotlivé roky a jejich hodnoty dostat ze sloupců do řádků. Tuto tranformaci nám zajistí funkce `load_data` a výsledek se uloží do parametru `data` třídy `EurostatCrimeTable`. 

Při zavolání funkce `filter_data` se nám data vyfiltrují a automaticky dopočítají statistické ukazatele a souhrnné informace pro zadanou zemi a trestný čin. Filtrování jsme si usnadnili pomocí `ipywidgets`, abychom nemuseli kod neustále ručně neefektivně přepisovat.

Kriminálí činny byly roztřízeny do tří kategorií dle toho, jak moc jsou viditelné, odhalitelné a v podstatě často hlášené:

- visible
- sensitive
- hidden

S jejich pomocí pak můžeme relevatněji interpretovat data, protože růst visible činnů bude znamenat růst zvýšeného výskytu, kdežto u sensitiv kategorie to bude znamenat, že docházi k častějšímu nahlašování. 

Během práce s daty nám vznikly tři způsoby použití kódu:

1) Práce v [interaktivním jupyter notebooku](notebooks/crime_analysis_by_country.ipynb), který za nás filtruje data, vykresluje graf a poskytuje základní popis dat. S filtrovanými daty můžeme pod interaktivní částí dále pracovat, jednoduše se dostaneme i k základnímu přetransforovanému datasetu, ve kterém jsou všechny země a trestné činny, který se ukrývá pod parametrem `data` třídy `EurostatCrimeTable`.
2) Pro lepší vizualizace a hlubší pochopení celkového kontextu dat pro jednotlivé země a kriminální čin(y) byl nakonec vytvořen přehledový Dash data dashboard pomocí využívající Plotly. Pro jeho spuštění je potřeba spustit aplikaci `python app.py`
3) Pro zkoumání souhrnných číselných údajů lze použít [běžný jupyter notebook](notebooks/summarized_crime_info.ipynb). 

Během spuštěné aplikace `app.py` je doporučeno nespouštět i interaktivni ipywidgets, protože může dojít ke kolizi a mohou se "duplikovat" grafy v notebooku. 

## Jak pracovat s repozitářem a jak spustit Dash aplikaci

Po naklonování repozitáře otevřete [requiremets](requirements.txt) a dle pokynů v něm si nainstalujte virtuální prostřední, aktivujte ho a naistalujte závislosti. 

Po instalaci je možné si spustit jupyter notebooky ve složce notebooks a to buď [interaktivní notebook](notebooks/crime_analysis_by_country.ipynb) zaměřující se na kombinaci země a vybraný kriminální čin, nebo [sumarizační notebook](notebooks/summarized_crime_info.ipynb) zaměřující se hodnocení vypočtených ukazatelů pro všechny země a jejich kriminální činny.

Spuštěním `python app.py` se Vám spustí sumarizační dashboard na adrese [http://127.0.0.1:8050/](http://127.0.0.1:8050/), který ukazuje pokročilejší vizualizace. 

## Questions & Feedback

Kontaktovat mě můžete na [LinkedIn](https://www.linkedin.com/in/klarabek/)



