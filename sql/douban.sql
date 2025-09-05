/*
 Navicat Premium Data Transfer

 Source Server         : localhost_3306
 Source Server Type    : MySQL
 Source Server Version : 80036 (8.0.36)
 Source Host           : localhost:3306
 Source Schema         : douban

 Target Server Type    : MySQL
 Target Server Version : 80036 (8.0.36)
 File Encoding         : 65001

 Date: 05/09/2025 09:34:42
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for author
-- ----------------------------
DROP TABLE IF EXISTS `author`;
CREATE TABLE `author`  (
  `author_id` bigint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '作者id',
  `author_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '作者名字',
  `nation` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '中国' COMMENT '国籍',
  PRIMARY KEY (`author_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 66 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '作者信息表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for book_tag
-- ----------------------------
DROP TABLE IF EXISTS `book_tag`;
CREATE TABLE `book_tag`  (
  `book_id` bigint NOT NULL COMMENT '书id',
  `book_tag` char(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '书标签',
  PRIMARY KEY (`book_id`, `book_tag`) USING BTREE,
  INDEX `booktag_tags`(`book_tag` ASC) USING BTREE,
  CONSTRAINT `bookid_book` FOREIGN KEY (`book_id`) REFERENCES `cleaned_douban_books` (`book_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `booktag_tags` FOREIGN KEY (`book_tag`) REFERENCES `tags` (`tag`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for cleaned_douban_books
-- ----------------------------
DROP TABLE IF EXISTS `cleaned_douban_books`;
CREATE TABLE `cleaned_douban_books`  (
  `book_id` bigint NOT NULL COMMENT '书籍编号',
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '书名',
  `img_src` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '封面图片链接',
  `author_id` bigint UNSIGNED NULL DEFAULT NULL COMMENT '作者id',
  `publisher` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '出版社',
  `producer` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '出品方',
  `original_title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '原作名',
  `translator` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '译者',
  `publication_year` date NULL DEFAULT NULL COMMENT '出版年份',
  `page_count` int NULL DEFAULT NULL COMMENT '页数',
  `price` decimal(10, 2) NULL DEFAULT NULL COMMENT '定价',
  `binding` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '装帧',
  `series` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '所属系列',
  `isbn` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT 'ISBN编号',
  `rating` decimal(3, 1) NULL DEFAULT NULL COMMENT '评分（平均分）',
  `rating_sum` int NULL DEFAULT NULL COMMENT '评分人数',
  `stars5_starstop` decimal(5, 2) NULL DEFAULT NULL COMMENT '五星比例（%）',
  `stars4_starstop` decimal(5, 2) NULL DEFAULT NULL COMMENT '四星比例（%）',
  `stars3_starstop` decimal(5, 2) NULL DEFAULT NULL COMMENT '三星比例（%）',
  `stars2_starstop` decimal(5, 2) NULL DEFAULT NULL COMMENT '二星比例（%）',
  `stars1_starstop` decimal(5, 2) NULL DEFAULT NULL COMMENT '一星比例（%）',
  PRIMARY KEY (`book_id`) USING BTREE,
  INDEX `book_id`(`book_id` ASC, `author_id` ASC) USING BTREE,
  INDEX `AB`(`author_id` ASC) USING BTREE,
  CONSTRAINT `AB` FOREIGN KEY (`author_id`) REFERENCES `author` (`author_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '豆瓣图书清洗后数据表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for comments
-- ----------------------------
DROP TABLE IF EXISTS `comments`;
CREATE TABLE `comments`  (
  `comment_id` bigint UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '评论的唯一标识符',
  `book_id` bigint NOT NULL COMMENT '关联的书籍ID',
  `user_link` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '用户标识',
  `comment_file` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '评论内容',
  `comment_star` tinyint UNSIGNED NOT NULL COMMENT '评论给出的星级评分(1-5星)',
  `useful` int UNSIGNED NOT NULL DEFAULT 0 COMMENT '标记“有用”的数量',
  `comment_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '评论时间',
  `comment_place` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '评论地点',
  PRIMARY KEY (`comment_id`) USING BTREE,
  INDEX `BC`(`book_id` ASC) USING BTREE,
  CONSTRAINT `BC` FOREIGN KEY (`book_id`) REFERENCES `cleaned_douban_books` (`book_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `comments_chk_1` CHECK (`comment_star` between 1 and 5)
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '存储书籍评论信息' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for tags
-- ----------------------------
DROP TABLE IF EXISTS `tags`;
CREATE TABLE `tags`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `main_tag` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `tag` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `tag`(`tag` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 152 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;
