#!/usr/bin/env python
import sys
from com.process.KeywordHyperlinkProcess import *
from com.process.VersionHyperlinkProcess import *
from com.process.ProvisionHyperlinkProcess import *
from com.process.ManualHyperlinkProcess import *
from com.process.AbbreviationHyperlinkProcess import *
from com.process.filter import *
from com.util.lexismail import *
from com.util.lexismsg import *
from com.transfer.transfer import *
from com.process.rollback import *


if __name__=='__main__':
	khp=KeywordHyperlinkProcess.KeywordHyperlinkProcess()
	vhp=VersionHyperlinkProcess.VersionHyperlinkProcess()
	phprocess=ProvisionHyperlinkProcess.ProvisionHyperlinkProcess()
	mhp=ManualHyperlinkProcess.ManualHyperlinkProcess()
	ahp=AbbreviationHyperlinkProcess()
	
	#backup data
	backupData()

	#initial phase	 
	try:
		khp.initial()	
		#sendNotification(LexisMsg.MSG_INITIAL_FINISHED)	
	except Exception,e:
		khp.log.error(e)
		sendNotification(LexisMsg.MSG_INITIAL_FAILED)	
		sys.exit()

	#process phase
	try:
		for queueItem in khp.queueDao.getAll():
			khp.begin(queueItem)
			article=khp.getArticle(queueItem)
			backupArticle(article)
			if article and article.content:
				khp.log.info("Hyperlink processing article type:%s id:%s" % (queueItem.contentType,queueItem.targetId))
				article=khp.process(article)
				article=vhp.process(article)
				article=ahp.process(article)
				article=phprocess.process(article)
				article=mhp.process(article)
				khp.updateArticle(article)
			else:
				khp.log.warning("Article type:%s id:%s was not found" %(queueItem.contentType,queueItem.targetId))
			khp.end(queueItem)
		
		for queueItem in khp.queueDao.getByContentTypeStatus(Article.CONTENT_TYPE_LAW,Article.STATUS_WAIT_UPLOAD):
			article=phprocess.getArticle(queueItem)
			if article and article.content:
				article.content=phprocess.removeProvisionRelativeArticleLink(article.content)
				phprocess.addProvisionRelativeArticleLink(article)
			else:
				khp.log.warning("Article type:%s id:%s was not found" %(queueItem.contentType,queueItem.targetId))
		#sendNotification(LexisMsg.MSG_PROCESS_FINISHED)	
	except Exception,e:
		khp.log.error(e)
		sendNotification(LexisMsg.MSG_PROCESS_FAILED)	
		sys.exit()
		
	#transfer phase 
	try:
		#transferData()
		#sendNotification(LexisMsg.MSG_TRANSFER_FINISHED)	
		pass
	except Exception,e:
		khp.log.error(e)
		sendNotification(LexisMsg.MSG_TRANSFER_FAILED)	
		sys.exit()

	sendNotification(LexisMsg.MSG_HYPERLINK_FINISHED)	
	
