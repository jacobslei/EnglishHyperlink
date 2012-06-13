#coding=utf-8
from com.entity.Case import *
from com.dao import *
class CaseDAO(DAO):
	"case create,read,update and delete"
	
	def __init__(self):
		DAO.__init__(self)
	
	def getAll(self):
		"获取所有有效案例"
		try:
			self.cursor_stg.execute("SELECT case_id,title,origin_id,provider_id,isEnglish FROM cases WHERE isEnglish='Y' AND display=1;")
			for row in self.cursor_stg.fetchall():
				case=Case()
				case.id=row[0]
				case.title=row[1]
				case.originId=row[2]
				case.providerId=row[3]
				case.isEnglish=row[4]
				yield case	
		except Exception,e:
			self.log.error(e)

	def getById(self,id):
		"根据主键信息获取案例"
		article=Case()	
		try:
			self.cursor_stg.execute("SELECT cases.case_id as id,cases.title,case_content.content,cases.origin_id,cases.provider_id,cases.isEnglish FROM cases LEFT JOIN case_content ON cases.case_id=case_content.case_id WHERE cases.case_id=%s;" % id)
			row=self.cursor_stg.fetchone()
			if row:
				article.id=row[0]
				article.title=row[1]
				article.content=row[2]
				article.originId=row[3]
				article.providerId=row[4]
				article.isEnglish=row[5]
			else:
				raise Exception("No case with id %s found!" %id)
		except Exception,e:
			self.log.error(e)	
		return article

	def getByKey(self,originId,providerId,isEnglish):
		"根据origin_id,provider_id,isEnglish获取案例"
		self.cursor_stg.execute("SELECT cases.case_id,cases.title,case_content.content FROM cases LEFT JOIN case_content ON cases.case_id=case_content.case_id WHERE cases.origin_id=%s AND cases.provider_id=%s AND cases.isEnglish='%s'" % (originId,providerId,isEnglish))
		row =self.cursor_stg.fetchone()
		case=Case()
		case.id=row[0]
		case.title=row[1]
		case.content=row[2]
		case.originId=originId
		case.providerId=providerId
		case.isEnglish=isEnglish
		return case	

	def updateContent(self,article):
		"update content and in_time"
		#TODO optimize merge following two sql statement
		article.content=article.content.replace("'","\\'")
		article.content=article.content.replace('"','\\"')
		#print "CaseDAO updateContent()UPDATE case_content SET content='%s'" % article.content
		self.cursor_stg.execute("UPDATE case_content SET content='%s' WHERE case_id=%s" % (article.content,article.id))


	def updateTime(self,article):
		self.cursor_stg.execute("UPDATE cases SET cases.in_time=NOW() WHERE case_id=%s" % article.id)

	def update(self,article):
		self.updateContent(article)
		self.updateTime(article)
		

if __name__=='__main__':
	caseDao=CaseDAO()
	for case in caseDao.getAll():
		print case.title
