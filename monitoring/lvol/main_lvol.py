from lvol import LvolsMonitor

lvols = LvolsMonitor()
lvols.update()

lvols.get_all()
print(lvols.get_item('/',"lvol.part.available"))
