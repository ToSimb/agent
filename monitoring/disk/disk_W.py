from .disk_WL import get_disk_data

def all_disk():
    return get_disk_data()

if __name__ == "__main__":
    print(all_disk())