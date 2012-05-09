//
//  STConfiguration.h
//  Stamped
//
//  Created by Landon Judkins on 4/11/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>

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
