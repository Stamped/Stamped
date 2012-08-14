//
//  STConfiguration.h
//  Stamped
//
//  Created by Landon Judkins on 4/11/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

/*
 A generic configuration system that supports in app modification and change exporting.
 
 The configuration system supports convenient registration and access to named values,
 with a number of convenience methods for particular types of values like flags, colors, fonts, etc.
 In addition, the configuration system provides a controller hiearchy for modifying these values
 from inside of an app session. In many cases, value access is also written to support dynamic loading
 of these updated values for rapid experimentation by non-iOS staff. The system also features, change
 summarization and email based export for reporting change requests.
 
 Notes:
 This system has seen mixed success. Mostly, its use was disgarded in many places by Devin, and
 in the rush of v2 preparations I didn't use it much in new views. Also, non-iOS staff use was limited
 and many features were discovered late or not at all. I'm sure that I ever received a change-list email.
 I would consider cutting or deprecating this system based on lack of use in practice. However, it
 could be handy if used, especially with BE driven configuration.
 
 2012-08-10
 -Landon
 */

#import <Foundation/Foundation.h>

extern NSString* const STConfigurationValueDidChangeNotification;

@interface STConfigurationItem : NSObject

- (id)initWithValue:(id)value key:(NSString*)key andSection:(NSString*)section;
- (UITableViewCell*)tableViewCellWithTableView:(UITableView*)tableView;
- (CGFloat)tableViewCellHeightWithTableView:(UITableView*)tableView;
- (void)wasSelectedInTableView:(UITableView*)tableView atIndexPath:(NSIndexPath*)indexPath;

@property (nonatomic, readonly, copy) NSString* key;
@property (nonatomic, readonly, copy) NSString* section;
@property (nonatomic, readwrite, retain) id value;
@property (nonatomic, readonly, retain) id originalValue;
@property (nonatomic, readwrite, copy) NSString* description;
@property (nonatomic, readonly, copy) NSString* displayValue;
@property (nonatomic, readonly, assign) BOOL modified;

@end

@interface STConfiguration : NSObject

+ (STConfiguration*)sharedInstance;

- (NSInteger)internalVersion;

- (id)objectForKey:(NSString*)key;

- (NSArray*)modifiedKeys;

- (NSString*)modificationReport;

+ (id)value:(NSString*)key;

+ (BOOL)flag:(NSString*)key;

- (NSArray*)keys;

- (UIViewController*)controller;

- (void)resetValues;

- (void)addConfigurationItem:(STConfigurationItem*)item;

+ (void)addValue:(id)value forKey:(NSString*)key inSection:(NSString*)section;

+ (void)addFont:(UIFont*)font forKey:(NSString*)key inSection:(NSString*)section;

+ (void)addString:(NSString*)string forKey:(NSString*)key inSection:(NSString*)section;

+ (void)addNumber:(NSNumber*)number forKey:(NSString*)key inSection:(NSString*)section;

+ (void)addColor:(UIColor*)color forKey:(NSString*)key inSection:(NSString*)section;

+ (void)addFlag:(BOOL)flag forKey:(NSString*)key inSection:(NSString*)section;

+ (void)addChoices:(NSDictionary*)choices originalKey:(NSString*)originalKey forKey:(NSString*)key inSection:(NSString*)section;

+ (void)addPoint:(NSValue*)point forKey:(NSString*)key inSection:(NSString*)section;

+ (void)addValue:(id)value forKey:(NSString*)key;

+ (void)addFont:(UIFont*)font forKey:(NSString*)key;

+ (void)addString:(NSString*)string forKey:(NSString*)key;

+ (void)addNumber:(NSNumber*)number forKey:(NSString*)key;

+ (void)addColor:(UIColor*)color forKey:(NSString*)key;

+ (void)addFlag:(BOOL)flag forKey:(NSString*)key;

+ (void)addPoint:(NSValue*)point forKey:(NSString*)key;

+ (void)addChoices:(NSDictionary*)choices originalKey:(NSString*)originalKey forKey:(NSString*)key;

@end
