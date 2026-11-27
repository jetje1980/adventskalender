# Family Crazy Adventskalender

Digitale adventskalender voor gezinnen, op adventscalender.app. Eigenaar: Griëtte (Vonck Communicatie). Mede-beheerder: Duurt.
Taal in code, commentaar en app: Nederlands, informeel (je/jij). Toon van de inhoud: kort en hard, mild voor kinderen onder 13.

## Opbouw
- `kalender.html` is de bron; `python3 bouw.py` maakt er `index.html` van. Na elke wijziging opnieuw bouwen.
- `films/` filmpjes, `kamers/` kamertjes. Beeld is nu gemaakt van winkelfoto's: alleen voor eigen gebruik, niet voor verkoop.
- `supabase/advent/index.ts` is de serverfunctie (Supabase-project family-crazy-advent). Wijzigingen daar worden apart gedeployed.

## Vaste regels
- Persoonsgegevens, foto's en video's van het gezin komen nooit in deze repo; alleen in Supabase (database of kluis `advent-media`).
- Elke wijziging die gegevens raakt, gaat langs de skill `privacy-bewaker`.
- Gezinsleden zien alleen hun eigen raampjes en geen toekomstige; die controle zit in de serverfunctie, niet alleen in de app.
- Geen tracking, geen externe scripts of fonts behalve Google Fonts zonder dat de privacy-bewaker het heeft getoetst.
- Agents in `.claude/agents/` bereiden voor en controleren; Griëtte beslist.
