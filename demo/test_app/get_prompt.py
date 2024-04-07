import nltk
from nltk.tokenize import word_tokenize


def process_prompt(input_text):

    prompt_text = f"""
    "You are a MySQL expert. Given an input question, first create a syntactically correct SQL
    Query to run, then look at the results of the query and return the answer to the input question.
    You must query only the columns that are needed to answer the question.
    Pay attention to use only the column names you can see in the tables below. Be careful to not query for columns that do not exist.
    Pay attention to which columns is in which table.
    Pay attention to that the constraint variables are case sensitive and must match the columns name.
    Pay attention to return an executable sql query.
    Pay attention to that the values of variables need to be enclosed in quotation marks, for example: 
    it should be ' SELECT col_1 FROM Table_69d3e454334311e9831e542696d6e445
    WHERE col_7 < abc ' instead of 'SELECT col_1 FROM Table_69d3e454334311e9831e542696d6e445 WHERE col_7 < \"abc\"'.
    Pay attention to that SQL tables need to be given aliases when using join, for example: 
    it should be 'SELECT a.name FROM actor AS a JOIN cast AS c ON a.aid = c.aid JOIN
    movie AS m ON c.msid = m.mid WHERE m.title = '霸王别姬\" AND c.role = '程蝶衣'' 
    instead of 'SELECT actor.name FROM actor JOIN cast ON actor.aid = cast.aid JOIN
    movie ON cast.msid = movie.mid WHERE movie.title = '霸王别姬' AND cast.role = '程蝶衣''.
    
    Output the final SQL query only.
        
    Use the following format:
    SQLQuery:  SQL Query here.
    Only use the following tables:
    
    CREATE TABLE \"school_detail\" (\"admissions\" TEXT, \"answerurl\" TEXT, \"belong\" TEXT, \"central\" TEXT, 
    \"city_id\" TEXT, \"city_name\" TEXT, \"code_enroll\" TEXT, \"colleges_level\" TEXT, \"county_id\" TEXT, 
    \"county_name\" TEXT, \"department\" TEXT, \"doublehigh\" TEXT, \"dual_class\" TEXT, \"dual_class_name\" TEXT, 
    \"f211\" INTEGER, \"f985\" INTEGER, \"hightitle\" TEXT, \"inner_rate\" TEXT, \"is_recruitment\" TEXT, \"level\" TEXT, 
    \"level_name\" TEXT, \"name\" TEXT, \"nature\" TEXT, \"nature_name\" TEXT, \"outer_rate\" TEXT, \"province_id\" TEXT, 
    \"province_name\" TEXT, \"rank\" TEXT, \"rank_type\" TEXT, \"rate\" TEXT, \"school_id\" INTEGER, \"school_type\" TEXT, 
    \"tag_name\" TEXT, \"type\" TEXT, \"type_name\" TEXT, \"view_month\" TEXT, \"view_total\" TEXT, \"view_total_number\" TEXT, 
    \"view_week\" TEXT, \"short\" TEXT, \"old_name\" TEXT, \"proid\" TEXT);
     
     /*The table school_detail description is: '学校详情'.
    The school_id field of school_detail means 学校ID and has possible values as: ['99', '51', '78', '98', '135'].
    The admissions field of school_detail means 强基计划 and has possible values as: ['1', '2'].
    The answerurl field of school_detail means 招生办网址(官方招生咨询平台) and has possible values as: 
    ['https://answer.eol.cn/fillmess/index?id=1439&source=zsgk_app', 'https://answer.eol.cn/fillmess/index?id=699&source=zsgk_app', 
    'https://answer.eol.cn/fillmess/index?id=1479&source=zsgk_app', 'https://answer.eol.cn/fillmess/index?id=871&source=zsgk_app', 
    'https://answer.eol.cn/fillmess/index?id=621&source=zsgk_app'].
    The belong field of school_detail means 隶属(学校属于哪个组织或机构) and has possible values as: ['北京', '中国人民大学', '河北省', '南昌大学', '中国社会科学院'].
    The central field of school_detail means 中央部委 and has possible values as: ['1', '2'].
    The city_id field of school_detail means 学校所在城市的ID and has possible values as: ['3701', '3708', '1401', '3702', '3501'].
    The city_name field of school_detail means 学校所在城市的名称 and has possible values as: ['北京市', '太原市', '深圳市', '唐山市', '天津市'].
    The code_enroll field of school_detail means 招生代码 and has possible values as: ['1111700', '1024600', '1024800', '1000600', '1024700'].
    The colleges_level field of school_detail means 学校层次,(省级示范、国家级骨干等) and has possible values as: 
    ['76001,76004', '76004,76005', '76002,76004', '76002,76004,76005,76006', '76005,76006'].
    The county_id field of school_detail means 学校所在区县的ID and has possible values as: ['370112', '370212', '370211', '0', '350211'].
    The county_name field of school_detail means 学校所在区县的名称 and has possible values as: ['昌平区', '海淀区', '丰台区', '朝阳区', '西城区'].
    The department field of school_detail means 学校所在部门 and has possible values as: ['1', '2'].
    The doublehigh field of school_detail means 双高计划 and has possible values as: ['0', '77001', '77002', '77005', '77003'].
    The dual_class field of school_detail means 双一流代码(38000(一流学科建设高校)38001(一流大学建设高校A类) 38002(一流大学建设高校B类)) and has possible values as: ['38001', '38000', '38003'].
    The dual_class_name field of school_detail means 双一流学科名称 and has possible values as: ['双一流', ''].
    The f211 field of school_detail means 211工程 and has possible values as: ['1', '2'].
    The f985 field of school_detail means 985工程 and has possible values as: ['1', '2'].
    The hightitle field of school_detail means 高校名称 and has possible values as: ['清华大学', '北京大学', '中山大学', '北京理工大学', '北京工业大学'].
    The inner_rate field of school_detail means 内部排名 and has possible values as: ['42.00', '0', '34.98', '62.90', '51.51'].
    The is_recruitment field of school_detail means 是否招生 and has possible values as: ['1', '2'].
    The level field of school_detail means 教育等级, \"普通本科\":2001, \"专科（高职）\": 2002 and has possible values as: ['2001', '2002'].
    The level_name field of school_detail means 办学层次名称 and has possible values as: ['普通本科', '专科（高职）'].
    The name field of school_detail means 学校名称 and has possible values as: ['清华大学', '北京大学', '中山大学', '北京理工大学', '北京工业大学'].
    The nature field of school_detail means 办学类型，36000: \"公办\", 36001: \"民办\" and has possible values as: ['36001', '0', '36000', '36002', '36004'].
    The nature_name field of school_detail means 办学类型名称 and has possible values as: ['独立学院', '内地与港澳台地区合作办学', '中外合作办学', '境外高校独立办学', '民办'].
    The outer_rate field of school_detail means 外部排名 and has possible values as: ['0', '11.99', '6.99', '9.00', '5.51'].
    The province_id field of school_detail means 学校所在省份的ID and has possible values as: ['51', '21', '82', '62', '64'].
    The province_name field of school_detail means 学校所在省份的名称 and has possible values as: ['北京', '河北', '黑龙江', '天津', '辽宁'].
    The rank field of school_detail means 学校排名 and has possible values as: .
    The rank_type field of school_detail means 学校排名类型 and has possible values as: .
    The rate field of school_detail means 学校评分 and has possible values as: ['0', '93.99', '97.43', '93.98', '83.69'].
    The school_type field of school_detail means 办学类型：\"普通本科\": \"6000\",\"专科（高职)\": , 6002: \"独立学院\", 6003: \"中外合作办学\", 6007: \"其他\" and has possible values as: ['6000', '6001'].
    The tag_name field of school_detail means 学校类型名称 and has possible values as: ['教育部直属', '中央部委院', ''].
    The type field of school_detail means 学校类型 and has possible values as: ['0', '5000', '5008', '5011', '5012'].
    The type_name field of school_detail means 学校的类型，以及类型的名称 and has possible values as: ['理工类', '财经类', '艺术类', '师范类', '体育类'].
    The view_month field of school_detail means 学校浏览量(月) and has possible values as: ['9852', '8421', '6717', '8298', '16317'].
    The view_total field of school_detail means 学校浏览量(总) and has possible values as: ['1848.2w', '365.5w', '1882.2w', '666.1w', '233.1w'].
    The view_total_number field of school_detail means 学校浏览量(总数) and has possible values as: ['18240400', '18822155', '13361474', '21135078', '13385154'].
    The view_week field of school_detail means 学校浏览量(周) and has possible values as: ['360', '888', '363', '600', '1428'].
    The short field of school_detail means 学校简称 and has possible values as: ['北京清华,清华', '清华大学医学部,协和医学院', 'pku,北大', '中国石油大学北京,北京中国石油大学,石油大学北京,北京石油大学', '北京中国地质大学,中国地质大学北京,CUGB'].
    The old_name field of school_detail means 学校旧名称 and has possible values as: ['北洋大学', '清华大学医学部', '佛山大学', '华南工学院', '北京工业学院'].
    The proid field of school_detail means 学校项目ID and has possible values as: ['51', '21', '82', '62', '64']. 
           
    */ 
    \"Question\": \"{input_text}\",
    \"SQLQuery\": 
    """

    return prompt_text

    # # Tokenize the prompt text
    # tokens = word_tokenize(prompt_text)
    #
    # # Count the number of tokens
    # num_tokens = len(tokens)
    #
    # print(num_tokens)
    #
    # return prompt_text


# if __name__ == "__main__":
#     process_prompt("北京大学在哪里？")