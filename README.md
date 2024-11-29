# Kriminalita v zemích EU

## Cíl projektu
Cílem projektu je automatizace zpracování dat o kriminalitě v zemích EU a jejich statistická analýza. Projekt se zaměřuje na identifikaci extrémů v kriminalitních činech v jednotlivých státech a sledování jejich dlouhodobých trendů. Projekt poskytne podklad pro zodpovězení klíčových otázek, jako například: Které země EU čelí největším výkyvům v kriminalitě? Jaké trestné činy jsou nejvíce na vzestupu?

## Práce s datasetem a doporučené postupy
Pro správnou práci s datasetem je nezbytné prostudovat dostupnou [dokumentaci](https://ec.europa.eu/eurostat/cache/metadata/en/crim_sims.htm) a [doporučení](https://ec.europa.eu/eurostat/documents/3859598/18846431/KS-GQ-24-010-EN-N.pdf/ef737587-085e-6018-8038-e41f59222020?version=3.0&t=1712826948630) od Eurostatu. Tím se minimalizuje riziko nesprávného použití dat a následné chybné interpretace výsledků.

Zpracován je základní dataset *Police-recorded offences by offence category (crim_off_cat)* z kategorie *Police-recorded offences (crim_off)* z [databáze Crime and criminal justice](https://ec.europa.eu/eurostat/web/crime/database) z Eurostatu.

### Příprava dat a číselníků
Číselníky pro rozkódování kriminálních činů a zemí byly vytvořeny za pomoci Pythonu. Raw data byla manuálně extrahována z tabulek základního datasetu v menu (bohužel nebyl nalezen lepší zdroj). Následně byla data vyčištěna a číselníky uloženy ve formátu `.csv` ve složce [data](/data).

## Důležité poznámky k interpretaci dat
1. **Významné změny mezi roky**  
   Eurostat zveřejňuje data pouze tehdy, pokud jsou potvrzena jednotlivými zeměmi. Extrémní výkyvy tak pravděpodobně odrážejí skutečné změny, nikoli chyby v publikaci dat.

2. **Rozdíly v legislativě**  
   Některé činy mohou být v jedné zemi klasifikovány jako přestupky, zatímco v jiné jako trestné činy. Proto je nejvhodnější srovnávat trendy v čase namísto absolutních úrovní kriminality mezi státy.

3. **Srovnatelnost států**  
   Pokud chcete srovnávat jednotlivé země, je nutné podrobně prostudovat dokumentaci a analyzovat, které státy lze srovnávat pro konkrétní kriminální činy. Legislativa a metodika sběru dat se totiž mezi státy liší, i přes snahy o standardizaci.

4. **Podkategorie v datech**  
   Dataset obsahuje podkategorie, které ponecháváme k dispozici pro detailnější analýzu. V případě potřeby je možné je odfiltrovat. Mezi podkategorie patří:
   - **Sexual violence**: Rape, Sexual assault
   - **Sexual exploitation**: Child pornography
   - **Burglary**: Burglary of private residential premises
   - **Theft**: Theft of a motorized vehicle or parts thereof
   - **Corruption**: Bribery

### Omezení dostupnosti dat

Od roku 2019 přestaly poskytovat data následující země:
- **Scotland**
- **England and Wales**
- **Northern Ireland**


## Metodika a postup zpracování dat

### Transformace dat

Dataset se ukázal být bohatý na informace, ale ve své původní podobě špatně interpretovatelný, což si vyžádalo rozsáhlou transformaci. Při prvotním zpracování se ukázalo, že kvůli četným manipulacím a statistickým výpočtům je kód špatně čitelný a znovupoužitelný, a tedy i neefektivní. Z tohoto důvodu byl vytvořen nový přístup, který řeší tyto problémy pomocí objektově orientovaného programování.

Celé zpracování základního datasetu je nyní uzavřeno do třídy `EurostatCrimeTable`, která se referenčně odkazuje na třídu `Statistics`. Třída `Statistics` automatizuje výpočet důležitých ukazatelů a zpracování výjimek. Pomocí funkce `create_summary_df_1all()` třídy `EurostatCrimeTable` lze snadno vytvořit souhrnný dataframe, který nabízí klíčové informace bez nutnosti grafické vizualizace.

### Kroky transformace

Transformace dat zahrnuje ve zkratce následující kroky:
1. **Načtení dat**: Dataset se načte a uloží pomocí funkce `load_data`.
2. **Rozdělení sloupců**: První složený sloupec je rozdělen na jednotlivé sloupce.
3. **Rozkódování dat**: Číselné kódy trestných činů a názvy zemí jsou rozkódovány.
4. **Vyčistění dat a přetypovaní dat** 
4. **Filtrování údajů**: Zachována jsou pouze data přepočítaná na 100 tisíc obyvatel každé země.
5. **Unpivotování dat**: Jednotlivé roky a jejich hodnoty jsou transformovány ze sloupců do řádků. Tento výsledek je uložen do parametru `data` třídy `EurostatCrimeTable`.

### Automatizace filtrování a analýzy

Pomocí funkce `filter_data` lze dataset filtrovat podle země a trestného činu. Tato funkce zároveň automaticky dopočítá statistické ukazatele a souhrnné informace. Pro zjednodušení filtrování bylo použito `ipywidgets`, což eliminuje nutnost ručního přepisování kódu.

### Kategorizace trestných činů

Trestné činy byly roztříděny do tří kategorií podle jejich viditelnosti, odhalitelnosti a frekvence hlášení:
- **Visible**: Trestné činy, jejichž růst obvykle indikuje zvýšený výskyt.
- **Sensitive**: Trestné činy, jejichž růst naznačuje častější hlášení.
- **Hidden**: Trestné činy, které jsou obtížně odhalitelné a méně často hlášené.

Tato kategorizace umožňuje přesnější interpretaci trendů v datech.


## Způsoby použití kódu

Během práce s daty byly vytvořeny tři hlavní způsoby použití kódu:

1. **Interaktivní Jupyter notebook**  
   Notebook [crime_analysis_by_country.ipynb](notebooks/crime_analysis_by_country.ipynb) umožňuje:
   - Filtraci dat
   - Vizualizaci grafů
   - Poskytnutí základního popisu dat  
   Filtrovaná data jsou dostupná pro další analýzu a transformovaný dataset je přístupný přes parametr `data` třídy `EurostatCrimeTable`.

2. **Dash Data Dashboard**  
   Přehledový dashboard byl vytvořen pomocí Dash a Plotly pro hlubší vizualizaci a pochopení dat. Spustíte jej příkazem:
   ```bash
   python app.py

3. **Souhrnný Jupyter notebook**

    Notebook [summarized_crime_info.ipynb](notebooks/summarized_crime_info.ipynb) umožňuje zkoumání souhrnných číselných údajů.


## Jak pracovat s repozitářem a jak spustit Dash aplikaci

1. **Naklonování repozitáře**  
   Po naklonování repozitáře otevřete soubor [requirements.txt](requirements.txt). Postupujte podle pokynů v souboru:
   - Nastavte virtuální prostředí.
   - Aktivujte virtuální prostředí.
   - Nainstalujte závislosti uvedené v souboru.

2. **Spuštění Jupyter notebooků**  
   Po instalaci závislostí můžete pracovat s notebooky ve složce `notebooks`:
   - **[Interaktivní notebook](notebooks/crime_analysis_by_country.ipynb)**  
     Tento notebook je zaměřený na analýzu kombinace vybrané země a kriminálního činu.
   - **[Sumarizační notebook](notebooks/summarized_crime_info.ipynb)**  
     Tento notebook slouží k hodnocení vypočtených ukazatelů pro všechny země a kriminální činy.

3. **Spuštění Dash aplikace**  
   Dashboard můžete spustit pomocí příkazu níže, který Vám spustí sumarizační dashboard na adrese [http://127.0.0.1:8050/](http://127.0.0.1:8050/), který ukazuje pokročilejší vizualizace:
   ```bash
   python app.py


## Questions & Feedback

Kontaktovat mě můžete na [LinkedIn](https://www.linkedin.com/in/klarabek/)



