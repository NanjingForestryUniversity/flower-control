# 一个数据库程序，能够使用devs.py去读取传感器的各项数值以及相应的植物状态图片
from devs import pump_once, read_status
import sqlite3
import time


from config import PICTURE_DIRECTORY, DATABASE_LOCATION, PICTURE_INTERVAL

# 创建数据库和图片文件夹
def create_img_dir():
    # create a directory for storing pictures
    if not os.path.exists(PICTURE_DIRECTORY):
        os.makedirs(PICTURE_DIRECTORY)


def create_table():
    """
    Create table if not exists
    """
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS data (
        time text,
        img_path text,
        temp real,
        vwc real,
        ec real,
        salinity real,
        tds real,
        epsilon real
    )""")
    conn.commit()
    conn.close()


# 增加数据到数据库
def insert_data(data: tuple):
    """
    Insert data into database

    :param data: tuple, (time, img_path, temp, vwc, ec, salinity, tds, epsilon)
    """
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO data VALUES (?, ?, ?, ?, ?, ?, ?, ?)", data)
    conn.commit()
    conn.close()


def save_img(img):
    """
    Save image to directory

    :param img: np.ndarray, image to save
    """
    img_path = os.path.join(PICTURE_DIRECTORY, str(time.time()) + ".jpg")
    cv2.imwrite(img_path, img)


# 删除表格中的某一个数据
def delete_data(time):
    """
    Delete data from database

    :param time: str, time of data to delete
    """
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    # find the corresponding image path
    c.execute("SELECT img_path FROM data WHERE time=?", (time,))
    img_path = c.fetchone()[0]
    # delete image
    delete_img(img_path)
    c.execute("DELETE FROM data WHERE time=?", (time,))
    conn.commit()
    conn.close()


# 删除相应的图片
def delete_img(img_path):
    """
    Delete image from directory

    :param img_path: str, path of image to delete
    """
    os.remove(img_path)


# 数据修改
def update_data(time, data: tuple):
    """
    Update data in database, attention, the image cannot be changed!

    :param time: str, time of data to update
    :param data: tuple, (time, img_path, temp, vwc, ec, salinity, tds, epsilon)
    """
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("UPDATE data SET time=?, temp=?, vwc=?, ec=?, salinity=?, tds=?, epsilon=? WHERE time=?", (data[0], data[2], data[3], data[4], data[5], data[6], data[7], time))
    conn.commit()
    conn.close()


# 读取数据库中的数据
def read_data():
    """
    Read data from database
    """
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM data")
    conn.close()
    return c.fetchall()


def read_recent_data(data_num):
    """
    Read recent data from database

    :param data_num: int, number of data to read
    """
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("SELECT * FROM data ORDER BY time DESC LIMIT ?", (data_num,))
    print(c.fetchall())
    conn.close()


def main():
    create_img_dir()
    create_table()
    while True:
        # read sensor data
        status = read_status()
        # take a picture
        img_path = take_picture()
        # insert data into database
        data = (time.time(), img_path, status['TEMP'], status['VWC'], status['EC'], status['SALINITY'], status['TDS'], status['EPSILON'])
        insert_data(data)
        # pump water
        pump_once()
        time.sleep(10)


if __name__ == "__main__":
    main()