<?php
try {
    $work_dir = '.';
    $file_list = scandir($work_dir);

    $all_section_detail = array();

    foreach ($file_list as $filename) {
        // 匹配{email}.json格式
        if (preg_match('/.+@.+\.json/', $filename)) {
            $json_string = file_get_contents($filename);
            $stu_stat = json_decode($json_string, true);
            foreach ($stu_stat['detail'] as $section_detail) {
                $section_name = $section_detail['name'];
                $section_score = $section_detail['score'];
                if (array_key_exists($section_name, $all_section_detail)) {
                    $all_section_detail[$section_name][] = $section_score;
                } else {
                    $all_section_detail[$section_name] = [$section_score];
                }
            }
        }
    }
    echo json_encode(array(
        'err' => 0,
        'res' => $all_section_detail,
    ));

} catch (Exception $e) {
    echo json_encode(array(
        'err' => 1,
        'msg' => $e->getMessage()
    ));
}
