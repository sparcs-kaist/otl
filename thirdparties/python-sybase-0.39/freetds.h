/******************************************************************

 Copyright 2001 by Object Craft P/L, Melbourne, Australia.

 LICENCE - see LICENCE file distributed with this software for details.

******************************************************************/

/* Only support back levels to 0.60
 */
#if HAVE_FREETDS < 60
#undef HAVE_FREETDS
#define HAVE_FREETDS 62
#endif

#define CS_USERNAME CS_USERNAME
#define CS_PASSWORD CS_PASSWORD
#define CS_APPNAME CS_APPNAME
#define CS_HOSTNAME CS_HOSTNAME
#define CS_PACKETSIZE CS_PACKETSIZE
#define CS_SEC_ENCRYPTION CS_SEC_ENCRYPTION
#define CS_LOC_PROP CS_LOC_PROP
#define CS_SEC_CHALLENGE CS_SEC_CHALLENGE
#define CS_SEC_NEGOTIATE CS_SEC_NEGOTIATE
#define CS_TDS_VERSION CS_TDS_VERSION
#define CS_NETIO CS_NETIO
#define CS_IFILE CS_IFILE
#define CS_USERDATA CS_USERDATA
#define CS_SEC_APPDEFINED CS_SEC_APPDEFINED
#define CS_CHARSETCNV CS_CHARSETCNV
#define CS_ANSI_BINDS CS_ANSI_BINDS
#define CS_VER_STRING CS_VER_STRING

#define CS_FMT_UNUSED CS_FMT_UNUSED
#define CS_FMT_NULLTERM CS_FMT_NULLTERM
#define CS_FMT_PADBLANK CS_FMT_PADBLANK
#define CS_FMT_PADNULL CS_FMT_PADNULL

#define CS_MONTH CS_MONTH
#define CS_SHORTMONTH CS_SHORTMONTH
#define CS_DAYNAME CS_DAYNAME
#define CS_DATEORDER CS_DATEORDER
#define CS_12HOUR CS_12HOUR
#define CS_DT_CONVFMT CS_DT_CONVFMT

#define CS_DATES_HMS CS_DATES_HMS
#define CS_DATES_SHORT CS_DATES_SHORT
#define CS_DATES_LONG CS_DATES_LONG
#define CS_DATES_MDY1 CS_DATES_MDY1
#define CS_DATES_MYD1 CS_DATES_MYD1
#define CS_DATES_DMY1 CS_DATES_DMY1
#define CS_DATES_DYM1 CS_DATES_DYM1
#define CS_DATES_YDM1 CS_DATES_YDM1
#define CS_DATES_YMD2 CS_DATES_YMD2
#define CS_DATES_MDY1_YYYY CS_DATES_MDY1_YYYY
#define CS_DATES_DMY1_YYYY CS_DATES_DMY1_YYYY
#define CS_DATES_YMD2_YYYY CS_DATES_YMD2_YYYY
#define CS_DATES_DMY2 CS_DATES_DMY2
#define CS_DATES_YMD1 CS_DATES_YMD1
#define CS_DATES_DMY2_YYYY CS_DATES_DMY2_YYYY
#define CS_DATES_YMD1_YYYY CS_DATES_YMD1_YYYY
#define CS_DATES_DMY4 CS_DATES_DMY4
#define CS_DATES_DMY4_YYYY CS_DATES_DMY4_YYYY
#define CS_DATES_MDY2 CS_DATES_MDY2
#define CS_DATES_MDY2_YYYY CS_DATES_MDY2_YYYY
#define CS_DATES_DMY3 CS_DATES_DMY3
#define CS_DATES_MDY3 CS_DATES_MDY3
#define CS_DATES_DMY3_YYYY CS_DATES_DMY3_YYYY
#define CS_DATES_MDY3_YYYY CS_DATES_MDY3_YYYY
#define CS_DATES_YMD3 CS_DATES_YMD3
#define CS_DATES_YMD3_YYYY CS_DATES_YMD3_YYYY

#ifndef CS_SRC_VALUE
#define CS_SRC_VALUE 0
#endif
#define CS_MAX_SCALE 77

#if HAVE_FREETDS < 61
typedef unsigned char CS_BIT;
typedef unsigned short CS_USHORT;
typedef unsigned char CS_BINARY;
typedef long CS_LONG;
typedef unsigned char CS_LONGCHAR;
typedef unsigned char CS_LONGBINARY;
typedef unsigned char CS_TEXT;
typedef unsigned char CS_IMAGE;
typedef CS_NUMERIC CS_DECIMAL;
#endif
#define CS_INTERNAL

/* Emulate Sybase inline error handling
 */
#ifndef CS_CLEAR
#define CS_CLEAR 35
#endif 
#define CS_INIT 36
#define CS_STATUS 37
#define CS_MSGLIMIT 38
#define CS_CLIENTMSG_TYPE 4700
#define CS_SERVERMSG_TYPE 4701
#define CS_ALLMSG_TYPE 4702

/* Define missing constants
 */
#ifndef CS_EXEC_IMMEDIATE
#define CS_EXEC_IMMEDIATE   (CS_INT)719
#endif

/* FreeTDS does not define these in their include files for some reason...
 */
CS_RETCODE blk_bind(CS_BLKDESC *blkdesc, CS_INT colnum, CS_DATAFMT *datafmt, CS_VOID *buffer, CS_INT *datalen, CS_SMALLINT *indicator);
CS_RETCODE blk_done(CS_BLKDESC *blkdesc, CS_INT type, CS_INT *outrow);
CS_RETCODE blk_drop(CS_BLKDESC *blkdesc);
CS_RETCODE blk_init(CS_BLKDESC *blkdesc, CS_INT direction, CS_CHAR *tablename, CS_INT tnamelen);
CS_RETCODE blk_props(CS_BLKDESC *blkdesc, CS_INT action, CS_INT property, CS_VOID *buffer, CS_INT buflen, CS_INT *outlen);
CS_RETCODE blk_rowxfer(CS_BLKDESC *blkdesc);

CS_RETCODE cs_convert(CS_CONTEXT *ctx, CS_DATAFMT *srcfmt, CS_VOID *srcdata, CS_DATAFMT *destfmt, CS_VOID *destdata, CS_INT *resultlen);
CS_RETCODE cs_ctx_alloc(CS_INT version, CS_CONTEXT **ctx);
CS_RETCODE cs_ctx_drop(CS_CONTEXT *ctx);
CS_RETCODE cs_dt_crack(CS_CONTEXT *ctx, CS_INT datetype, CS_VOID *dateval, CS_DATEREC *daterec);
CS_RETCODE cs_dt_info(CS_CONTEXT *ctx, CS_INT action, CS_LOCALE *locale, CS_INT type, CS_INT item, CS_VOID *buffer, CS_INT buflen, CS_INT *outlen);
CS_RETCODE cs_loc_alloc(CS_CONTEXT *ctx, CS_LOCALE **locptr);
CS_RETCODE cs_loc_drop(CS_CONTEXT *ctx, CS_LOCALE *locale);
CS_RETCODE cs_locale(CS_CONTEXT *ctx, CS_INT action, CS_LOCALE *locale, CS_INT type, CS_VOID *buffer, CS_INT buflen, CS_INT *outlen);

CS_RETCODE ct_bind(CS_COMMAND *cmd, CS_INT item, CS_DATAFMT *datafmt, CS_VOID *buffer, CS_INT *copied, CS_SMALLINT *indicator);
CS_RETCODE ct_callback(CS_CONTEXT *ctx, CS_CONNECTION *con, CS_INT action, CS_INT type, CS_VOID *func);
CS_RETCODE ct_cancel(CS_CONNECTION *conn, CS_COMMAND *cmd, CS_INT type);
CS_RETCODE ct_close(CS_CONNECTION *con, CS_INT option);
CS_RETCODE ct_cmd_alloc(CS_CONNECTION *con, CS_COMMAND **cmd);
CS_RETCODE ct_cmd_drop(CS_COMMAND *cmd);
CS_RETCODE ct_command(CS_COMMAND *cmd, CS_INT type, const CS_VOID *buffer, CS_INT buflen, CS_INT option);
CS_RETCODE ct_con_alloc(CS_CONTEXT *ctx, CS_CONNECTION **con);
CS_RETCODE ct_con_drop(CS_CONNECTION *con);
CS_RETCODE ct_con_props(CS_CONNECTION *con, CS_INT action, CS_INT property, CS_VOID *buffer, CS_INT buflen, CS_INT *out_len);
CS_RETCODE ct_config(CS_CONTEXT *ctx, CS_INT action, CS_INT property, CS_VOID *buffer, CS_INT buflen, CS_INT *outlen);
CS_RETCODE ct_connect(CS_CONNECTION *con, CS_CHAR *servername, CS_INT snamelen);
CS_RETCODE ct_data_info(CS_COMMAND *cmd, CS_INT action, CS_INT colnum, CS_IODESC *iodesc);
CS_RETCODE ct_describe(CS_COMMAND *cmd, CS_INT item, CS_DATAFMT *datafmt);
CS_RETCODE ct_exit(CS_CONTEXT *ctx, CS_INT unused);
CS_RETCODE ct_fetch(CS_COMMAND *cmd, CS_INT type, CS_INT offset, CS_INT option, CS_INT *rows_read);
CS_RETCODE ct_get_data(CS_COMMAND *cmd, CS_INT item, CS_VOID *buffer, CS_INT buflen, CS_INT *outlen);
CS_RETCODE ct_init(CS_CONTEXT *ctx, CS_INT version);
CS_RETCODE ct_options(CS_CONNECTION *con, CS_INT action, CS_INT option, CS_VOID *param, CS_INT paramlen, CS_INT *outlen);
CS_RETCODE ct_param(CS_COMMAND *cmd, CS_DATAFMT *datafmt, CS_VOID *data, CS_INT datalen, CS_SMALLINT indicator);
CS_RETCODE ct_res_info(CS_COMMAND *cmd, CS_INT type, CS_VOID *buffer, CS_INT buflen, CS_INT *out_len);
CS_RETCODE ct_results(CS_COMMAND *cmd, CS_INT *result_type);
CS_RETCODE ct_send(CS_COMMAND *cmd);
CS_RETCODE ct_send_data(CS_COMMAND *cmd, CS_VOID *buffer, CS_INT buflen);
