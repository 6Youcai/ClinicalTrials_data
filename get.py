#!/usr/bin/env python3

import re
import sys
import xml.etree.ElementTree as ET

class clinicaltrials(object):
    def __init__(self, XML):
        self.__tree = ET.parse(XML)
    @property
    def condition(self):
        """
        适应症
        """
        res = []
        for i in self.__tree.iterfind('condition'):
            res.append(i.text)
        return ";".join(res)
    @property
    def phase(self):
        """
        试验分期
        """
        return self.__tree.findtext('phase')
    @property
    def status(self):
        """
        招募状态
        """
        return self.__tree.findtext('overall_status')
    @property
    def enrollment(self):
        """
        预计招募病人数
        """
        return self.__tree.findtext('enrollment')
    @property
    def date(self):
        """
        Anticipated Study Start Date, Estimated Study Completion Date, Estimated Primary Completion Date
        """
        return self.__tree.findtext('start_date'), self.__tree.findtext('completion_date'), self.__tree.findtext('primary_completion_date')
    @property
    def sponsor(self):
        """
        Sponsor
        """
        res = []
        for i in self.__tree.iter('lead_sponsor'):
            res.append(i.find('agency').text)
        return "".join(res)
    @property
    def collaborator(self):
        """
        Collaborator
        """
        res = []
        for i in self.__tree.iter('collaborator'):
            res.append(i.find('agency').text)
        if len(res) == 0:
            return "Not Provided"
        return ";".join(res)
    @property
    def drug_name(self):
        """
        药品名称
        """
        res = []
        for i in self.__tree.iterfind('intervention'):
            drug = i.find('intervention_name').text
            res.append(drug)
        return ";".join(res)
    @property
    def official_title(self):
        """
        临床试验名称
        """
        return self.__tree.findtext('official_title')
    @property
    def overall_official(self):
        """
        研究者姓名  研究者单位
        """
        last_name = []
        affiliation = []
        for i in self.__tree.iterfind('overall_official'):
            last_name.append(i.find('last_name').text)
            try:
                affiliation.append(i.find('affiliation').text)
            except:
                # NCT03117049.xml
                affiliation.append("Not Provided")
        if len(last_name) == 0:
            return "Not Provided", "Not Provided"
        return ";".join(last_name), ";".join(affiliation)
    def outcome(self, mode):
        """
        终点指标    终点指标详述
        """
        measure = []
        time_frame = []
        # mode: primary_outcome, secondary_outcome
        for i in self.__tree.iterfind(mode):
            measure.append(i.find('measure').text)
            time_frame.append(i.find('time_frame').text)
        if len(measure) == 0:
            return "Not Provided", "Not Provided"
        details = list(zip(measure, time_frame))
        fn = lambda x: x[0] + "[ Time Frame: " + x[1] + " ]"
        details = list(map(fn, details))
        return ";".join(measure), ";".join(details)
    @property
    def inclusion(self):
        """
        入选标准
        """
        res = []
        for i in self.__tree.iterfind('eligibility'):
            text = i.find('criteria').find('textblock').text
            res.append(text)
        raw_text = ";".join(res)
        trim_enter = list(filter(lambda x: x!='', raw_text.split('\n')))
        trim_blank = list(map(lambda x:re.sub("^\s+", "", x), trim_enter))
        text = "".join(trim_blank)
        if re.search("Inclusion Criteria.*?Exclusion Criteria", text, re.IGNORECASE):
            # Inclusion Criteria
            inclusion_criteria = re.search("Inclusion Criteria:?(.*?)Exclusion Criteria", text, re.IGNORECASE).group(1)
            # Exclusion Criteria
            exclusion_criteria = re.search("Exclusion Criteria:?(.*)", text, re.IGNORECASE).group(1)
            # trim note
            exclusion_criteria = re.sub("Note:[^-]+", "", exclusion_criteria)
            return inclusion_criteria, exclusion_criteria
        elif re.search("Inclusion Criteria", text, re.IGNORECASE):
            inclusion_criteria = re.search("Inclusion Criteria:?(.*?)", text, re.IGNORECASE).group(1)
            return inclusion_criteria, "unknow Exclusion Criteria"
        else:
            return "unknow Inclusion Criteria", "unknow Exclusion Criteria"
    @property
    def url(self):
        """
        链接
        """
        res = []
        for i in self.__tree.iterfind('required_header'):
            res.append(i.find('url').text)
        return ";".join(res)

if __name__ == "__main__":

    # print("适应症", "试验分期", "招募状态", "已募集人数", "预计招募病人数", "Anticipated Study Start Date", \
    #       "Estimated Study Completion Date", "Estimated Primary Completion Date", "Sponsor", "Collaborator", \
    #       "药品名称", "临床试验名称", "研究者姓名", "研究者单位", "Biomarker", "检测合作方", "主要终点指标", \
    #       "主要终点指标详述", "次要终点指标", "次要终点指标详述", "入选标准", "排除标准", "结果公布", "链接", sep = '###')
    # sys.exit(0)
    record = clinicaltrials(sys.argv[1])

    dat1, dat2, dat3 = record.date
    name, organization = record.overall_official
    primary_measure, primary_frame = record.outcome('primary_outcome')
    secondary_measure, secondary_frame = record.outcome('secondary_outcome')
    inclusion_criteria, exclusion_criteria = record.inclusion

    print(record.condition, record.phase, record.status, "NA", record.enrollment, \
          dat1, dat2, dat3, record.sponsor, record.collaborator, record.drug_name, \
          record.official_title, name, organization, "NA", "NA", \
          primary_measure, primary_frame, secondary_measure, secondary_frame, \
          inclusion_criteria, exclusion_criteria, "NA", record.url, sep = '###')
