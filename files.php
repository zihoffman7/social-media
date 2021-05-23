<?php

function delete_directory($directory) {
  if (substr($directory, strlen($directory) - 1, 1) != "/") {
    $directory .= "/";
  }

  $files = glob($directory . "*", GLOB_MARK);

  foreach ($files as $file) {
    if (is_dir($file)) {
      delete_directory($file);
    }
    else {
      unlink($file);
    }
  }

  rmdir($directory);
}

function compress($source, $destination, $quality) {
  $info = getimagesize($source);

  if ($info["mime"] == "image/jpeg") {
    $image = imagecreatefromjpeg($source);
  }
  else if ($info["mime"] == "image/gif") {
    $image = imagecreatefromgif($source);
  }
  else if ($info["mime"] == "image/png") {
    $image = imagecreatefrompng($source);
  }

  $exif = exif_read_data($source);

  if (isset($exif["Orientation"])) {
    switch ($exif["Orientation"]) {
      case 3:
        $image = imagerotate($image, 180, 0);
        break;

      case 6:
        $image = imagerotate($image, 270, 0);
        break;

      case 8:
        $image = imagerotate($image, 90, 0);
        break;
    }

  }

  imagejpeg($image, $destination, $quality);
}

if ($argc > 1) {
  $json_data = $argv[1];
  $data = json_decode($json_data);
}

switch ($data->task) {
  case "delete dir":
    if (file_exists("uploads/" . $data->user)) {
      delete_directory("uploads/" . $data->user);
    }
    break;

  case "create dir":
    if (!file_exists("uploads/" . $data->user)) {
      mkdir("uploads/" . $data->user, 0777, true);
    }
    break;

  case "compress":
    compress($data->initial_path, $data->final_path, 50);
    break;
}

?>
