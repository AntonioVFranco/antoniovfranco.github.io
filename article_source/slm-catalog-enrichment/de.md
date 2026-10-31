# SLM-Fine-Tuning: Warum Marktplätze die Kosten ihrer Kataloganreicherung überdenken

Ein Marktplatz verarbeitet womöglich Millionen Produkte, um eine scheinbar einfache Frage zu beantworten: Was bietet jedes Produkt?

Stellen Sie sich eine Kaffeemaschine vor, deren Beschreibung einen Druck von 15 bar nennt. Damit Kunden sie mit anderen Produkten vergleichen können, muss der Marktplatz diese Information erkennen und das passende Katalogfeld ausfüllen. Das klingt nach wenig Arbeit. Multiplizieren Sie diesen Vorgang nun mit Millionen Angeboten, zu denen täglich neue Produkte und Änderungen hinzukommen.

Hier beginnt der Einsatz eines allgemeinen LLM für jede Extraktion das Budget zu belasten.

Drei Studien von Amazon-Teams zeigten 2026 einen anderen Weg. Kleinere, für Produktattribute angepasste Modelle senkten die Inferenzkosten deutlich. Die Studien zeigten auch, wo die Qualität sinkt und wie sich verhindern lässt, dass Einsparungen zusätzliche Prüfarbeit verursachen.

Katalogverantwortliche sollten nicht fragen, welches Modell besser schreibt. Entscheidend ist, was ein korrektes, sofort nutzbares Attribut kostet.

## Warum kostet die Anreicherung eines Katalogs so viel?

Wer mit Produktdaten gearbeitet hat, kennt das Problem. Lieferanten beschreiben Waren unterschiedlich, selbst innerhalb derselben Kategorie. Manche Informationen stehen im Titel, andere in der Beschreibung. Auch die verwendeten Begriffe sind nicht immer einheitlich.

Das wirkt sich unmittelbar auf den Einkauf aus. Ohne korrekt ausgefüllte Attribute finden Filter bestimmte Produkte nicht, Vergleiche verlieren an Nutzen und Kunden fällt die Entscheidung schwerer.

Sprachmodelle helfen, Beschreibungen in abfragbare Felder zu überführen. Problematisch wird es, wenn ein Unternehmen fast jede Aufgabe demselben allgemeinen Modell überlässt, auch Aufgaben, die sich kaum verändern.

Nehmen wir die Extraktion des Drucks aus Tausenden Kaffeemaschinen. Dafür müssen Wert und Einheit erkannt, das Katalogformat eingehalten und fehlende Angaben offengelassen werden. Das Modell muss dafür keine offene Unterhaltung über beliebige Themen führen können.

Selbst wenn die einzelne Inferenz günstig wirkt, wiederholt sie sich mit jedem Katalogwachstum und jeder Aktualisierung. Kleine Kosten pro Produkt können bei mehreren zehn Millionen Datensätzen ins Gewicht fallen.

Das Volumen verändert deshalb die Entscheidung. Je häufiger verarbeitet wird, desto sinnvoller ist die Untersuchung eines spezialisierten Modells.

## Was bedeutet es, ein SLM für Produktdaten zu trainieren?

SLM steht für *small language model*, also kleines Sprachmodell. Die Idee ist, ein Modell mit weniger Parametern an eine bestimmte Aufgabe anzupassen, etwa Produktattribute aus Beschreibungen zu extrahieren.

Beim Fine-Tuning erhält das Modell Beispiele für Eingaben und erwartete Ausgaben. Es lernt, wie der Vorgang ablaufen soll, welche Felder auszufüllen sind und wann ein Wert leer bleiben muss.

Eine dabei eingesetzte Technik ist LoRA. Sie trainiert weniger Parameter, statt sämtliche Modellgewichte zu aktualisieren. Das kann den Speicherbedarf beim Training senken. Es bedeutet für sich genommen nicht, dass die Inferenz 98 % günstiger wird. Die endgültigen Kosten hängen auch vom gewählten Modell und seiner Ausführung ab.

Eine weitere Möglichkeit ist, mit einem größeren Modell Trainingsbeispiele zu erzeugen und einen Teil seiner Fähigkeiten auf das kleinere zu übertragen. Dieses Verfahren heißt Destillation. Nach dem Training übernimmt das kleine Modell eine Aufgabe, die zuvor vom größeren abhing.

Praktisch konzentriert das Unternehmen die Anpassungsarbeit auf die Zeit vor dem Betrieb in großem Maßstab. Statt ständig für kaum genutzte Fähigkeiten zu bezahlen, führt es ein für den Prozess vorbereitetes Modell aus.

Das lohnt sich nur, wenn das gelernte Verhalten lange genug nützlich bleibt, um Training und Wartung auszugleichen. Die Ergebnisse aus 2026 helfen, dieses Potenzial einzuordnen.

## Eine Studie ermittelte 98 % niedrigere Inferenzkosten

Im Juli 2026 veröffentlichten Lakshman Kolasani und Fatemeh Taheri Dezaki [*Progressive Fine-Tuning for Cost-Effective Structured Attribute Generation in E-commerce*](https://aclanthology.org/2026.acl-industry.40/) im Industry Track der ACL.

Die Forschenden passten Amazon Nova 2 Lite mit LoRA an, um bei der Produkteinstellung Attribute zu generieren. Der wichtigste Vergleich erfolgte mit Claude Sonnet 4.5. Dieses Modell lieferte damals für die Aufgabe die besten Ergebnisse unter den vom Team untersuchten Modellen.

Für das angepasste Modell wurden **98 % niedrigere Inferenzkosten** geschätzt, berechnet anhand der öffentlichen Modellpreise zum Zeitpunkt der Experimente. Die p90-Latenz sank ebenfalls um etwa **70 %**. Die Zeitspanne, innerhalb der 90 % der Antworten abgeschlossen wurden, wurde also kürzer.

Die Untersuchung ging über interne Tests hinaus. In einem Versuch mit echten Nutzern lag die Annahmequote der Vorschläge des kleinen Modells bei **86,4 %**, gegenüber **88,3 %** bei Claude Sonnet 4.5.

Ein Detail darf nicht übersehen werden. Das kleinere Modell erreichte bei der Füllrate akzeptierter Attribute **59,1 %**, das größere **63,0 %**. Laut den Autoren waren die Unterschiede statistisch signifikant.

Die Einsparung ging somit nicht mit identischer Leistung im Produktivbetrieb einher. Unternehmen müssen bewerten, ob der Qualitätsunterschied die Kostensenkung rechtfertigt und wie sie mit Feldern umgehen, die das Modell nicht ausfüllen kann.

Die Arbeit liefert auch eine Idee für das Training: Neue Beispiele werden anhand von Informationen ausgewählt, die das Modell nicht extrahierte, obwohl sie im Katalog vorhanden waren. Statt den Trainingsdatensatz wahllos zu vergrößern, konzentrierte das Team die zweite Runde auf Fälle mit größeren Abständen zwischen Katalog und Vorhersage.

Mit zwei Runden von je tausend Beispielen stieg die gültige Füllrate in der Offline-Auswertung von 66,03 % auf 74,20 %. Das zeigte eine Verbesserung im verwendeten Testsatz, auch wenn das Modell im Produktivbetrieb hinter dem größeren zurückblieb.

Für einen Marktplatz lautet die Lehre: **Fehler im eigenen Katalog können helfen, die nächsten Trainingsdaten auszuwählen**. Vorhandene Inhalte müssen aber auf Richtigkeit geprüft werden, bevor sie als Referenz dienen.

## Eine andere Studie verarbeitete 30 Millionen Produkte für etwa 5.000 US-Dollar

Die im Oktober 2026 veröffentlichte Arbeit [*Scaling E-Commerce Attribute Extraction with Parallel Decoding*](https://aclanthology.org/2026.akbc-1.13/) von Nikhita Vedula und Kollegen untersuchte das Problem aus einem anderen Blickwinkel.

Das Team begann mit einer oft übersehenen Frage: Welche Attribute helfen Käufern tatsächlich, Produkte innerhalb einer Kategorie zu unterscheiden?

Zuerst bestimmt ein größeres Modell die relevanten Attribute. Anschließend extrahiert ein angepasstes Qwen3-4B die Werte aus den Beschreibungen. Das System nutzt *Hyper-Parallel Decoding* (HPD), um Werte mehrerer Attribute parallel statt vollständig nacheinander zu erzeugen.

Die Extraktionsgenauigkeit lag bei rund **85 %**, ähnlich wie beim größeren Referenzmodell. Eine menschliche Bewertung von 500 Produkten ergab eine ungefähr ebenso hohe Trefferquote.

Der Kostenunterschied zeigt sich bei der Verarbeitung von 30 Millionen Produkten:

| Untersuchte Konfiguration | Geschätzte Inferenzkosten | Geschätzte Zeit |
| --- | ---: | ---: |
| Referenz-LLM per Batch-API | 63.000 US-Dollar | Mehr als 300 Stunden, ohne Wartezeit in Warteschlangen |
| Qwen3-4B mit herkömmlicher Generierung | 46.000 US-Dollar | 333 Stunden |
| Qwen3-4B mit HPD | 5.000 US-Dollar | 36 Stunden |

Das sind die von den Autoren für ihre Konfiguration berichteten Werte, keine aktuellen Cloud-Angebote. Das Team schätzte außerdem etwa 350 US-Dollar für einen Fine-Tuning-Schritt mit acht A100-GPUs. Dieser Betrag umfasst nicht sämtliche Daten- und Entwicklungskosten.

Die Einsparung von **92 %** gegenüber dem Referenz-LLM fällt auf. Sie entstand allerdings nicht allein durch Fine-Tuning. Die Ausführung mit HPD war entscheidend. Dasselbe Qwen3-4B verursachte im Experiment mit herkömmlicher Attributgenerierung wesentlich höhere Kosten.

Der Vergleich zeigt, warum ein kleineres Modell nur ein Teil der Lösung ist. Ausgabeformat und Inferenzverfahren können die Kosten der Katalogverarbeitung erheblich verändern.

Die Studie verwendete englische Produkttexte. Für die direkte Anwendung auf portugiesische Kataloge ist eine eigene Bewertung nötig, insbesondere bei unvollständigen Beschreibungen oder abweichenden Einheitenkonventionen.

## Was passiert, wenn das kleine Modell Fehler macht?

Hier verlieren viele Einsparvorschläge ihre Überzeugungskraft.

Ein falsches Attribut kann Filter und Vergleiche beeinträchtigen. Müssen zu viele Datensätze von Hand geprüft werden, verlieren die geringeren Inferenzkosten ihren Wert.

Im Oktober 2026 untersuchte eine weitere Arbeit im Industry Track der EMNLP, [*When to Defer: Scope-Aware Cascades for Structured Attribute Generation in E-commerce Product Catalogs*](https://aclanthology.org/2026.emnlp-industry.187/), wie entschieden werden kann, welche SLM-Antworten akzeptiert werden.

Die Lösung berücksichtigte neben der Modellkonfidenz auch die jeweilige Aufgabe. Ein Modell kann bei einem Attribut häufig richtigliegen und bei einem anderen oft scheitern. Eine einzige Konfidenzschwelle für alles erfasst diesen Unterschied schlecht.

Mit einem Auswahlmechanismus, der Produkttyp und Attribut einbezieht, konnten die Forschenden **11,4 Prozentpunkte mehr Vorhersagen** akzeptieren als mit einer allgemeinen Schwelle. Die beobachtete Präzision blieb am betrachteten Auswertungspunkt bei **90,3 %**.

Das bedeutet nicht, dass das SLM 11,4 % präziser wurde. Der Vorteil lag darin, mehr Antworten zu nutzen, ohne die gemessene Präzision zu senken.

Die betriebliche Konsequenz ist wichtig. Das kleine Modell kann den Großteil des Volumens bearbeiten, während riskantere Fälle an eine Prüfung oder ein anderes Modell gehen. Nicht jeder Fehler verlangt ein größeres LLM: Manchmal bleibt ein Feld besser leer, bis genügend Informationen vorliegen.

Das teuerste Modell ist nicht für jedes Produkt nötig. Entscheidend ist, **wann die günstigere Antwort verwendet werden kann**.

## Wie erkennen Sie, ob sich Fine-Tuning für Ihren Marktplatz lohnt?

Beginnen Sie mit einer Kategorie, die viele neue Produkte erhält und regelmäßig Arbeit beim Ausfüllen oder Korrigieren verursacht. Messen Sie zunächst eine festgelegte Aufgabe, bevor die Lösung auf den gesamten Katalog ausgedehnt wird.

Trennen Sie Produkte für Training, Validierung und Test. Der Test muss Produkte enthalten, die das Modell während der Anpassung nicht gesehen hat, sowie Beschreibungen, die den aktuellen Datenverkehr abbilden. Sonst wirken die Ergebnisse besser, als sie im Betrieb sein werden.

Vergleichen Sie das bestehende System mit einem unangepassten SLM und demselben SLM nach dem Fine-Tuning. Bei Interesse an HPD oder anderen Inferenzverfahren sollten diese getrennt verglichen werden. So lässt sich der Trainingsgewinn vom Ausführungsgewinn unterscheiden.

Bewerten Sie anschließend pro Attribut, nicht nur pro Produkt. Ein Durchschnitt kann Fehler gerade in geschäftlich wichtigen Feldern verdecken. Messen Sie auch, wie viele Datensätze geprüft werden müssen und wie viele Felder leer bleiben.

Die wirtschaftliche Kennzahl muss die Lieferung eines korrekten, freigegebenen Attributs berücksichtigen, nicht nur die Erzeugung einer Antwort:

**Kosten pro freigegebenem Attribut = (Inferenz + Prüfung + Korrektur + Infrastruktur + amortisiertes Training) ÷ Anzahl korrekt freigegebener Attribute.**

Alle Kosten müssen denselben Zeitraum betreffen. Verteilen Sie das Training auf das Volumen, das bis zur nächsten Anpassung voraussichtlich verarbeitet wird.

Diese Rechnung verhindert einen häufigen Fehler: Ein Modell wegen günstigerer GPU-Kosten für billiger zu halten, ohne den Korrekturaufwand seiner Ausgaben zu berücksichtigen.

Bei häufigen Aktualisierungen und hohem Volumen ist ein angepasstes SLM eine interessante Alternative. Die Anfangsinvestition verteilt sich auf viele Extraktionen. Ein kleiner Katalog erzeugt womöglich nicht genug Einsparung für eine eigene Infrastruktur.

Das Ausbaukriterium ist objektiv. Liefert das SLM die benötigten Attribute, hält es die Fehlerquote innerhalb der betrieblichen Grenze und senkt es die Kosten pro freigegebenem Attribut, besteht eine Grundlage für mehr Einsatz.

## Der nächste Effizienzgewinn steckt vielleicht im Katalog, nicht in einem größeren LLM

Die Studien von 2026 zeigen, dass Produktanreicherung mit kleinen Modellen mehr als eine Labormöglichkeit ist. Es gibt Einführungsergebnisse, Kostenvergleiche und Verfahren zur Entscheidung, welche Antworten genutzt werden können.

Die Zahlen sind beachtlich: **98 % geschätzte Senkung der Inferenzkosten in einer Studie und 92 % in einer anderen**. Sie entstanden unter unterschiedlichen Bedingungen und sind kein Sparversprechen für jeden Marktplatz.

Die relevante Schlussfolgerung lautet anders. Sollen Attribute aus Millionen Produkten extrahiert werden, ist es sinnvoll, mit der Spezialisierung eines kleineren Modells zu beginnen, seine Qualität zu messen und die Ausführung zu optimieren. Ein allgemeines LLM in jeder Phase kann bedeuten, ständig für ungenutzte Fähigkeiten zu zahlen.

Wenn Ihr Unternehmen diese Entscheidung anhand eigener Daten, Volumen und Qualitätsanforderungen bewerten muss, arbeitet Huyawo Solutions an Modellauswahl und Anpassung für geschäftliche Probleme. Der Kontakt erfolgt schriftlich.

### Verwendete Studien und Dokumentation

1. [Kolasani und Dezaki, *Progressive Fine-Tuning for Cost-Effective Structured Attribute Generation in E-commerce*, ACL Industry Track, Juli 2026](https://aclanthology.org/2026.acl-industry.40/).
2. [Vedula und Kollegen, *Scaling E-Commerce Attribute Extraction with Parallel Decoding*, AKBC, Oktober 2026](https://aclanthology.org/2026.akbc-1.13/).
3. [Mansoori und Kollegen, *When to Defer: Scope-Aware Cascades for Structured Attribute Generation in E-commerce Product Catalogs*, EMNLP Industry Track, Oktober 2026](https://aclanthology.org/2026.emnlp-industry.187/).
4. [Hugging Face, LoRA-Dokumentation in PEFT](https://huggingface.co/docs/peft/v0.21.0/conceptual_guides/lora).
