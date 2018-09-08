# Buoy Acquisition Yolo
> A relatively janky but working custom object detection yolo model


Drone buoy acquisition model. 

## Step 1: Install (OS X & Linux)
```sh
python install -r requirements.txt
```

## Step 1.5: You may have to build the cython module with:
```
python setup.py build_ext --inplace
```

## Step 2: Download model checkpoints 

https://www.dropbox.com/sh/umc9m3ojzbd0glj/AAAkrO3G6BcrVax9euKJdsuia?dl=0

The models should live inside a folder labeled 'ckpt' in the root directory:

```
--ckpt
    |-- tiny-yolo-voc-1c-1375.data-00000-of-00001
    |-- tiny-yolo-voc-1c-1375.index
    |-- tiny-yolo-voc-1c-1375.meta
    |-- tiny-yolo-voc-1c-1375.profile

```

## Step 2: Run Server
```sh
python server.py
```

## Step 3: Run model + inferences
```sh
python video.py
```

## Usage example

Run python video.py. Starts OpenCV. Find the buoy. 


## Release History

* 0.0.1
    * Work in progress- model built on images taken from around the Foundry. We need to rebuild model from above- like drone footage- preferably on water

## Meta

Your Name – [@baykenney](https://twitter.com/baykenney) – mk365@duke.edu

[https://github.com/Duke-Ocean-XPrize/buoy-yolo-model](https://github.com/Duke-Ocean-XPrize/buoy-yolo-model)

## Contributing

1. Fork it (<https://github.com/Duke-Ocean-XPrize/buoy-yolo-model/fork>)
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request

