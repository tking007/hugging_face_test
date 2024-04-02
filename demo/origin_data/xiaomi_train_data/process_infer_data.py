import json
from process_train_data_for_Qwen import mean_pooling, encoder_decoder_1, model, tokenizer
from process_train_data_for_Qwen import gte_large_zh, model_1, tokenizer_1
import sqlite3
import os


def process_infer_data(infer_origin_data):

    instruction = """You are a MySQL expert. Given an input question, first create a syntactically correct SQL
    Query to run, then look at the results of the query and return the answer to the input question.
    You must query only the columns that are needed to answer the question.
    Pay attention to use only the column names you can see in the tables below. Be careful to not query for columns that do not exist.
    pay attention to which columns is in which table.
    Pay attention to that the constraint variables are case sensitive and must match the columns name.
    Pay attention to return an executable sql query.
    Pay attention to that the values of variables need to be enclosed in quotation marks, for example: it should be ' SELECT col_1 FROM Table_69d3e454334311e9831e542696d6e445
    WHERE col_7 < abc ' instead of 'SELECT col_1 FROM Table_69d3e454334311e9831e542696d6e445 WHERE col_7 < "abc"'.
    Pay attention to that SQL tables need to be given aliases when using join, for example: it should be 'SELECT a.name FROM actor AS a JOIN cast AS c ON a.aid = c.aid JOIN
    movie AS m ON c.msid = m.mid WHERE m.title = '霸王别姬" AND c.role = '程蝶衣'' instead of 'SELECT actor.name FROM actor JOIN cast ON actor.aid = cast.aid JOIN
    movie ON cast.msid = movie.mid WHERE movie.title = '霸王别姬' AND cast.role = '程蝶衣''.

    Output the final SQL query only.

    Use the following format:
    SQLQuery:  SQL Query here.
    Only use the following tables:

    CREATE TABLE "school_detail" ("admissions" TEXT, "answerurl" TEXT, "belong" TEXT, "central" TEXT, "city_id" TEXT, "city_name" TEXT, "code_enroll" TEXT,
        "colleges_level" TEXT, "county_id" TEXT, "county_name" TEXT, "department" TEXT, "doublehigh" TEXT, "dual_class" TEXT, "dual_class_name" TEXT, "f211" INTEGER,
        "f985" INTEGER, "hightitle" TEXT, "inner_rate" TEXT, "is_recruitment" TEXT, "level" TEXT, "level_name" TEXT, "name" TEXT, "nature" TEXT, "nature_name" TEXT,
        "outer_rate" TEXT, "province_id" TEXT, "province_name" TEXT, "rank" TEXT, "rank_type" TEXT, "rate" TEXT, "school_id" INTEGER, "school_type" TEXT, "tag_name" TEXT,
        "type" TEXT, "type_name" TEXT, "view_month" TEXT, "view_total" TEXT, "view_total_number" TEXT, "view_week" TEXT, "short" TEXT, "old_name" TEXT, "proid" TEXT);
        /*The table school_detail description is: '学校详情'.
    """

    means_dict = {'admissions': '强基计划', 'answerurl': '招生办网址(官方招生咨询平台)', 'belong': '隶属(学校属于哪个组织或机构)',
                    'central': '中央部委', 'city_id': '学校所在城市的ID', 'city_name': '学校所在城市的名称', 'code_enroll': '招生代码',
                    'colleges_level': '学校层次,(省级示范、国家级骨干等)', 'county_id': '学校所在区县的ID', 'county_name': '学校所在区县的名称',
                    'department': '学校所在部门', 'doublehigh': '双高计划', 'dual_class': '双一流代码(38000(一流学科建设高校)38001(一流大学建设高校A类) 38002(一流大学建设高校B类))',
                    'dual_class_name': '双一流学科名称', 'f211': '211工程', 'f985': '985工程', 'hightitle': '高校名称', 'inner_rate': '内部排名', 'is_recruitment': '是否招生',
                    'level': '教育等级, "普通本科":2001, "专科（高职）": 2002', 'level_name': '办学层次名称', 'name': '学校名称', 'school_image': '学校图片',
                    'nature': '办学类型，36000: "公办", 36001: "民办"', 'nature_name': '办学类型名称', 'outer_rate': '外部排名', 'province_id': '学校所在省份的ID',
                    'province_name': '学校所在省份的名称', 'rank': '学校排名', 'rank_type': '学校排名类型', 'rate': '学校评分', 'school_id': '学校ID',
                    'school_type': '办学类型："普通本科": "6000","专科（高职)": , 6002: "独立学院", 6003: "中外合作办学", 6007: "其他"',
                    'tag_name': '学校类型名称', 'type': '学校类型', 'type_name': '学校的类型，以及类型的名称',
                    'view_month': '学校浏览量(月)', 'view_total': '学校浏览量(总)', 'view_total_number': '学校浏览量(总数)', 'view_week': '学校浏览量(周)', 'short': '学校简称',
                    'old_name': '学校旧名称', 'proid': '学校项目ID', 'school_website': '学校网址', 'special_id': '专业类别ID', 'special_name': '专业类别名称',
                    'code': '专业类别带代码', 'major_id': '专业ID', 'major_name': '专业名称', 'degree': '专业学位', 'limit_year': '学制', 'major_rank': '专业排名', 'salaryavg': '专业平均工资',
                    'category_id': '专业分类ID', 'ruanke_level': '软科等级', 'ruanke_rank': '软科排名', 'school_name': '学校名称'}
    tables_meas = {'major_categories': '专业分类', 'major_school': '专业和学校关联表', 'majors': '专业详情', 'school_detail': '学校详情', 'schools': '专业开设学校'}

    prompts = []
    for line_dict in infer_origin_data:
        question = line_dict["question"]
        db_id = line_dict["db_id"]
        print(db_id)

        schema_info = f""

        # Connect to database and fetch table names and column names
        conn = sqlite3.connect(f'../../../test_get_gaokao_data/schools/{db_id}.sqlite')
        # conn = sqlite3.connect('actor_database.db')
        cursor = conn.cursor()

        # Get the filename that is connected above
        filename = conn.cursor().execute("PRAGMA database_list;").fetchall()[0][2]

        # Extract file name from file path
        database_name = os.path.basename(filename).split('.')[0]

        table_names = [table_info[0] for table_info in cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table';").fetchall()]

        # print(table_names)

        # Get column names and contents for each table
        table_to_score = {}
        for table_name in table_names:
            cursor.execute(f"SELECT * FROM `{table_name}` LIMIT 1")
            table_column_names = [description[0] for description in cursor.description]
            # print("111", table_column_names)
            table_contents = cursor.fetchone()
            table_description = tables_meas.get(table_name, table_name)
            table_column_contents = [f"{table_description} - {name}:{content}" for name, content in zip(table_column_names, table_contents)]
            # print("222", table_column_contents)

            # Find the highest matching score for this table
            highest_matching_score = gte_large_zh(question, table_column_contents, tokenizer_1, model_1)
            # print("333", highest_matching_score)

            # Record the highest matching score for this table
            table_to_score[table_name] = highest_matching_score

        # Find the table with the highest matching score
        highest_matching_table_name = max(table_to_score, key=table_to_score.get)
        print(f"The highest matching table name is: {highest_matching_table_name}")

        # for table_name in table_names:
        cursor.execute(f"PRAGMA table_info(`{highest_matching_table_name}`);")
        table_column_names = [column_info[1] for column_info in cursor.fetchall()]
        print(table_column_names)
        # 处理列名中的下划线，替换为空格
        # table_column_names = [column_name.replace("_", " ") for column_name in table_column_names]
        # column_names.extend(table_column_names)

        # print(table_column_names)
        # print(column_names)

        # highest_matching_table_name, highest_matching_table_column_names = encoder_decoder_1(
        #     question, table_names, tokenizer, model, cursor)

        schema_column = ""
        # print(table_names, column_names)

        for column_name in table_column_names:
            # print(column_name_original, table_name_original, column_type)
            cursor.execute(f"SELECT  DISTINCT `{column_name}` FROM `{highest_matching_table_name}` LIMIT 100")
            # print(column_name_original, table_name_original, db_id)
            possible_values = [str(row[0]) for row in cursor.fetchall()]
            # print(possible_values)

            if len(possible_values) == 0 or possible_values == ['']:
                highest_matching_column_info = ''
                highest_matching_column_info_2 = ''
            else:
                # print("sss", possible_values)
                highest_matching_column_info = encoder_decoder_1(question, possible_values, tokenizer, model)[:5]
                highest_matching_column_info_2 = gte_large_zh(question, possible_values, tokenizer_1, model_1)[:5]
                # print("@@@", highest_matching_column_info)

            column_name_original = column_name.replace("_", " ")
            means_str = means_dict.get(f'{column_name}', f"{column_name_original}")
            schema_column += f"The {column_name} field of {highest_matching_table_name} means {means_str} and has possible values as: {highest_matching_column_info_2}.\n"

        schema_info = f"""
        {schema_column}
        */"""

        conversation = f"""
        "Question": {question}
        "SQLQuery": 
        """

        prompt = f"{instruction} {schema_info} {conversation}"

        prompts.append(prompt)
        conn.close()

    return prompts


if __name__ == '__main__':
    # infer_origin_data = []
    # with open("infer.txt", "r", encoding='utf-8') as f:
    #     for line in f:
    #         infer_origin_data.append(json.loads(line))
        # for line in f:
        #     line_dict = json.loads(line)
        #     question = line_dict["question"]
        #     db_id = line_dict["db_id"]

    # # Convert to training data
    # infer_data = process_infer_data(infer_origin_data, instruction)
    #
    # # Write the training data to a new JSON file
    # with open("infer_data_for_Qwen.json", "w", encoding="utf-8") as f:
    #     json.dump(infer_data, f, ensure_ascii=False, indent=2)
    #
    # print("Done!")

    process_infer_data(input_text)