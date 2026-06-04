---
title: "Warum ich Staging und Produktion auf zwei Proxmox-Knoten getrennt habe"
date: 2026-06-02
description: "Wie aus einer einzelnen Proxmox-Installation eine getrennte Infrastruktur für Staging und Produktion wurde."
---

Als ich 2021 die Domain **lavallee.tech** registrierte, war mein Ziel einfach: lernen, experimentieren und einige Dienste für lokale Vereine bereitstellen.
Damals reichte ein einzelner Proxmox-Knoten auf einem gebrauchten Dell OptiPlex vollkommen aus. Ich betrieb einige YunoHost-VMs, hostete Webseiten und stellte Cloud- sowie E-Mail-Dienste für mehrere Vereine bereit.
Fünf Jahre später sieht die Infrastruktur deutlich anders aus.
Was als kleines Self-Hosting-Projekt begann, entwickelte sich nach und nach zu einer Plattform mit Produktivsystemen, Entwicklungsumgebungen, Monitoring-Lösungen und eigenen Anwendungen.
Dieses Wachstum zwang mich schließlich dazu, die gesamte Architektur neu zu überdenken.

![Vorher-Nachher-Architektur: Von einem einzelnen Proxmox-Knoten zu einer Trennung von Staging und Produktion](/images/articles/proxmox-staging-production/before-after-proxmox.png)

_Die Infrastruktur vor und nach der Trennung von Staging- und Produktionsumgebung._

## Die ursprüngliche Infrastruktur

Die Plattform lief ursprünglich auf einem Dell OptiPlex 3040 mit einem Intel i5-6500 und 16 GB Arbeitsspeicher.
Mehrere Jahre lang lief auf diesem System alles:

* Cloud- und E-Mail-Dienste für lokale Vereine
* Nextcloud- und Matrix-Installationen
* WordPress-Websites
* Monitoring-Systeme
* Entwicklungsprojekte
* Produktivanwendungen

Die Einfachheit einer Ein-Knoten-Infrastruktur hatte ihren Reiz. Es gab nur einen Server zu verwalten und die Ressourcen waren leicht überschaubar.
Solange die Anzahl der Dienste begrenzt blieb, funktionierte dieses Modell erstaunlich gut.

## Wenn Wachstum zum Problem wird
Die erste große Veränderung war die Einführung eines echten Staging- und Produktions-Workflows.
Anfangs hostete ich lediglich einige WordPress-Websites. Deployments waren unkompliziert und Änderungen direkt auf Produktivsystemen stellten kaum ein Risiko dar.
Das änderte sich, als ich begann, eigene Anwendungen zu entwickeln und bereitzustellen.
Ein Monitoring-Stack wurde eingeführt.
Eine Reverse-Proxy-Infrastruktur kam hinzu.
Die Website lavallee.tech wurde zu einem eigenständigen Projekt.
Eine Anwendung zum Streaming von IP-Kameras wurde bereitgestellt.
Eine französische Plattform für elektronische Rechnungen ging in die Entwicklung.
Jedes neue Projekt benötigte nun sowohl eine Produktions- als auch eine Staging-Umgebung.
Mit der Zeit wuchs die Infrastruktur auf rund zwanzig virtuelle Maschinen an.
Spätestens zu diesem Zeitpunkt waren die Grenzen der ursprünglichen Hardware nicht mehr zu übersehen.

## Der Arbeitsspeicher wird zum Engpass
Der Dell OptiPlex 3040 unterstützt maximal 16 GB RAM.
Heute laufen auf diesem Knoten:

* 1 AzuraCast-VM
* 1 VM für das Proxmox-Monitoring
* 4 YunoHost-VMs für lokale Vereine
* 2 WordPress-VMs
* 1 Reverse-Proxy-VM für die Produktion
* 1 VM für lavallee.tech
* 1 VM für das Facturier-Projekt
* 1 VM für das Kamera-Streaming
* Die entsprechenden Staging-Umgebungen
* 2 Monitoring-VMs für die Anwendungsplattform
* 1 Ansible-Kontrollknoten

Das deutlichste Zeichen dafür, dass die Infrastruktur ihre Grenzen erreicht hatte, war die Tatsache, dass die Staging-Umgebung nicht mehr dauerhaft betrieben werden konnte.
Um die Stabilität der Produktivsysteme sicherzustellen, musste ich sämtliche Staging-VMs abschalten.
Selbst mit rund zehn ausgeschalteten virtuellen Maschinen lag die Speicherauslastung weiterhin bei etwa 80 Prozent.
Eine Erweiterung des Arbeitsspeichers war nicht mehr möglich, da die Hardware bereits ihre maximale Kapazität erreicht hatte.
Die Infrastruktur war dem ursprünglichen Server schlichtweg entwachsen.

## Warum ein zweiter Proxmox-Knoten?
Anstatt die bestehende Hardware zu ersetzen, entschied ich mich für einen zweiten Proxmox-Knoten.
Der neue Server ist ein Dell OptiPlex 7010 mit einem Intel i7-3770 und 32 GB Arbeitsspeicher.
Ich habe bewusst erneut auf eine gebrauchte Workstation gesetzt.
Viele Homelab-Projekte konzentrieren sich auf Enterprise-Hardware, doch für meine Workloads ist die verfügbare Speicherkapazität häufig wichtiger als reine CPU-Leistung.
Gebrauchte Dell-OptiPlex-Systeme sind günstig, zuverlässig, kompakt und leicht verfügbar.
Vor allem bieten sie ein ausgezeichnetes Preis-Leistungs-Verhältnis für selbst betriebene Infrastruktur.
Durch den zweiten Knoten steigt die verfügbare Gesamtspeicherkapazität sofort von 16 GB auf 48 GB, ohne dass die Kosten aus dem Ruder laufen.

## Trennung von Staging und Produktion
Das Hauptziel des neuen Knotens besteht darin, Staging- und Produktions-Workloads physisch voneinander zu trennen.
Zuvor liefen beide Umgebungen auf derselben Hardware.
Das funktionierte in der Anfangsphase des Projekts gut, wurde jedoch mit zunehmender Anzahl von Anwendungen immer schwieriger zu verwalten.
Die neue Architektur ist deutlich einfacher:
![Proxmox-Datacenter mit Zwei-Knoten-Architektur](/images/articles/proxmox-staging-production/proxmox-two-nodes.png)

_Das aktuelle Proxmox-Datacenter. Produktions- und Staging-Workloads sind nun auf zwei physische Server verteilt._

| Knoten | CPU | RAM | Zweck |
|---------|---------|---------|---------|
| Dell OptiPlex 3040 | Intel i5-6500 | 16 GB | Produktion |
| Dell OptiPlex 7010 | Intel i7-3770 | 32 GB | Staging |

### Produktionsknoten

* Vereinsdienste
* Nextcloud
* Matrix
* WordPress-Websites
* Öffentlich erreichbare Anwendungen
* Reverse-Proxy-Dienste

### Staging-Knoten

* Anwendungsentwicklung
* Deployment-Tests
* Infrastrukturvalidierung
* Experimentelle Projekte

Diese Trennung sorgt für eine bessere Isolation der Ressourcen und ermöglicht es, die Staging-Umgebung dauerhaft verfügbar zu halten.
Noch wichtiger ist jedoch, dass der Deployment-Prozess nun deutlich näher an professionellen Produktionsumgebungen liegt.

## Weg von einigen YunoHost-Installationen
YunoHost spielte eine wichtige Rolle beim Wachstum der Plattform.
Es ermöglichte die schnelle Bereitstellung von Diensten wie Nextcloud und Matrix und war ein hervorragender Einstieg in die Welt des Self-Hostings.
Mit zunehmender Größe der Infrastruktur wurden jedoch einige Einschränkungen sichtbar.
Jede YunoHost-Instanz benötigt eine eigene virtuelle Maschine und verbraucht deutlich mehr Arbeitsspeicher als eine containerisierte Lösung.
Auch das Monitoring mehrerer YunoHost-Systeme wird mit wachsender Infrastruktur zunehmend komplex.
Deshalb nutze ich diese Umstrukturierung, um ausgewählte Kollaborationsdienste auf Docker-Deployments umzustellen, die über Ansible verwaltet werden.
Ziel ist nicht, YunoHost vollständig zu ersetzen, sondern dort auf flexiblere Deployment-Methoden zu setzen, wo es sinnvoll ist.

## Aufbau eines zentralen Monitorings
Ein weiterer wichtiger Grund für die Umstrukturierung ist die Observability.
Mit jeder neuen Anwendung und jeder zusätzlichen virtuellen Maschine wurde das Monitoring fragmentierter.
Im Laufe der Zeit entstanden mehrere Monitoring-Lösungen, darunter ein eigener Stack für Proxmox sowie separate Monitoring-Umgebungen für verschiedene Anwendungen.
Langfristig soll das Monitoring auf einer zentralen Plattform basierend auf Prometheus, Grafana und Loki konsolidiert werden.
Anstatt jede Umgebung einzeln zu überwachen, soll die gesamte Infrastruktur an einem Ort sichtbar sein.
Dadurch werden Fehlersuche und Analyse vereinfacht, die Transparenz erhöht und der Ressourcenverbrauch besser nachvollziehbar.

## Vorbereitung auf zukünftige Projekte
Die Infrastruktur wird gleichzeitig auf zukünftige Anwendungen vorbereitet.
Eines der wichtigsten laufenden Projekte ist eine französische Plattform für elektronische Rechnungen, die Factur-X-Rechnungen aus PDF-Dokumenten erzeugt.
Diese Anwendung benötigt eine echte Staging-Umgebung, in der neue Funktionen sicher getestet werden können, bevor sie in Produktion gehen.
Eine dedizierte Staging-Infrastruktur beseitigt dabei einen wesentlichen Engpass im Entwicklungsprozess und ermöglicht schnellere Weiterentwicklungen.

## Ausblick
Bei diesem Projekt geht es nicht einfach darum, mehr Arbeitsspeicher bereitzustellen.
Es ist eine Gelegenheit, eine Infrastruktur neu zu gestalten, die sich seit 2021 erheblich weiterentwickelt hat.
Aus einer kleinen Self-Hosting-Umgebung für lokale Vereine wurde eine Plattform mit Produktivsystemen, Entwicklungsumgebungen, Monitoring-Lösungen und eigenen Anwendungen.
Durch die Trennung von Staging und Produktion, die Migration ausgewählter Dienste auf Docker und den Aufbau einer zentralen Monitoring-Plattform wird die Infrastruktur einfacher zu betreiben, leichter zu erweitern und besser auf zukünftiges Wachstum vorbereitet.
Der ursprüngliche Dell OptiPlex 3040 hat seine Aufgabe bemerkenswert gut erfüllt.
Die Erweiterung um einen zweiten Proxmox-Knoten ist lediglich der nächste Schritt in der Weiterentwicklung der Plattform.
