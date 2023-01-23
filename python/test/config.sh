
get_config() {
    config=$1
    param=$2
    def_val=$3
    echo $($py -c "import sys, json; j = json.load(open('$config', 'r')); print( j['$param'] if '$param' in j else $def_val )")
}
