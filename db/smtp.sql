

/*
 * Please provide DATABASE name (I am using my_database which is created by default)
 */

/*
 * Mails
 */
CREATE TABLE my_database.mailitem (
	id VARCHAR(36) NOT NULL PRIMARY KEY,
	dateSent DATETIME,
	fromAddress VARCHAR(50) NOT NULL,
	toAddressList VARCHAR(1024) NOT NULL,
	subject VARCHAR(255),
	xmailer VARCHAR(50),
	body TEXT,
	contentType VARCHAR(50),
	boundary VARCHAR(255)
) ENGINE=MyISAM;

/*
 * Attachment
 */
CREATE TABLE my_database.attachment (
	id VARCHAR(36) NOT NULL PRIMARY KEY,
	mailItemId VARCHAR(36) NOT NULL,
	fileName VARCHAR(255),
	contentType VARCHAR(50),
	content TEXT
) ENGINE=MyISAM;