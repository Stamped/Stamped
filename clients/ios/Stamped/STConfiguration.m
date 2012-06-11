//
//  STConfiguration.m
//  Stamped
//
//  Created by Landon Judkins on 4/11/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STConfiguration.h"
#import "STTableViewController.h"
#import "Util.h"
#import "UIFont+Stamped.h"
#import "STDebugDatumViewController.h"
#import "STDebug.h"

NSString* const STConfigurationValueDidChangeNotification = @"STConfigurationValueDidChangeNotification";

@interface STConfigurationSectionController : STTableViewController <UITableViewDataSource, UITableViewDelegate>

- (id)initWithSection:(NSString*)section;

@property (nonatomic, readonly, copy) NSString* section;

@end

@implementation STConfigurationItem

@synthesize section = section_;
@synthesize key = key_;
@synthesize value = value_;
@synthesize originalValue = originalValue_;
@synthesize description = description_;


- (id)initWithValue:(id)value key:(NSString*)key andSection:(NSString*)section {
    self = [super init];
    if (self) {
        key_ = [key copy];
        section_ = [section copy];
        value_ = [value retain];
        originalValue_ = [value retain];
    }
    return self;
}

- (void)dealloc
{
    [section_ release];
    [key_ release];
    [value_ release];
    [originalValue_ release];
    [description_ release];
    [super dealloc];
}

- (UITableViewCell*)tableViewCellWithTableView:(UITableView*)tableView {
    //UITableViewCellStyle style = self.description ? UITableViewCellStyleSubtitle : UITableViewCellStyleValue1;
    UITableViewCell* cell = [[[UITableViewCell alloc] initWithStyle:UITableViewCellStyleSubtitle reuseIdentifier:@"TODO"] autorelease];
    cell.textLabel.text = self.key;
    cell.textLabel.font = [UIFont stampedFontWithSize:12];
    cell.detailTextLabel.text = self.displayValue;
    if (self.modified) {
        cell.detailTextLabel.textColor = [UIColor redColor];
    }
    
    return cell;
}

- (CGFloat)tableViewCellHeightWithTableView:(UITableView*)tableView {
    return 50;
}

- (void)wasSelectedInTableView:(UITableView*)tableView atIndexPath:(NSIndexPath*)indexPath {
    
}

- (NSString *)displayValue {
    return [NSString stringWithFormat:@"%@",self.value];
}

- (BOOL)modified {
    return ![self.originalValue isEqual:self.value];
}

@end

@interface STConfigurationStringItem : STConfigurationItem

@property (nonatomic, readwrite, copy) id (^fromString)(NSString* string);
@property (nonatomic, readwrite, copy) NSString* (^toString)(id value);
@property (nonatomic, readwrite, copy) NSString* (^errorMessageForString)(NSString* string);

@end

@implementation STConfigurationStringItem

@synthesize fromString = fromString_;
@synthesize toString = toString_;
@synthesize errorMessageForString = errorMessageForString_;

- (id)initWithValue:(id)value key:(NSString*)key andSection:(NSString*)section 
{
    self = [super initWithValue:value key:key andSection:section];
    if (self) {
        self.fromString = ^(NSString* string) {
            return string;
        };
        self.toString = ^(id value) {
            return [NSString stringWithFormat:@"%@", value];
        };
    }
    return self;
}

- (void)dealloc
{
    self.toString = nil;
    self.fromString = nil;
    self.errorMessageForString = nil;
    [super dealloc];
}

- (void)wasSelectedInTableView:(UITableView*)tableView atIndexPath:(NSIndexPath*)indexPath {
    [Util textInputWithDefault:self.toString(self.value) andCallback:^(NSString *string) {
        if (string) {
            id value = self.fromString(string);
            if (value) {
                self.value = value;
                [[NSNotificationCenter defaultCenter] postNotificationName:STConfigurationValueDidChangeNotification object:self.key];
                [tableView reloadData];
            }
            else {
                [Util warnWithMessage:[NSString stringWithFormat:@"%@ is not a valid value", string] andBlock:nil];
            }
        }
    }];
}

- (NSString *)displayValue {
    return self.toString(self.value);
}

@end

@interface STConfigurationMultipleChoiceItem : STConfigurationItem

- (id)initWithValue:(id)value key:(NSString*)key section:(NSString*)section andChoices:(NSDictionary*)choices;

@property (nonatomic, readonly, retain) NSDictionary* choices;

@end

@implementation STConfigurationMultipleChoiceItem

@synthesize choices = choices_;

- (id)initWithValue:(id)value key:(NSString*)key section:(NSString*)section andChoices:(NSDictionary*)choices {
    self = [super initWithValue:value key:key andSection:section];
    if (self) {
        choices_ = [choices retain];
    }
    return self;
}

- (void)dealloc
{
    [choices_ release];
    [super dealloc];
}

- (void)wasSelectedInTableView:(UITableView*)tableView atIndexPath:(NSIndexPath*)indexPath {
    [Util menuWithTitle:@"Choose Value" message:nil choices:[self.choices allKeys] andBlock:^(NSString *string) {
        if (string) {
            [[NSNotificationCenter defaultCenter] postNotificationName:STConfigurationValueDidChangeNotification object:self.key];
            self.value = [self.choices objectForKey:string];
            [tableView reloadData];
        }
    }];
}

- (NSString *)displayValue {
    for (NSString* key in [self.choices allKeys]) {
        id value = [self.choices objectForKey:key];
        //NSLog(@"Comparing %@ to %@",value, self.value);
        if ([value isEqual:self.value]) {
            return key;
        }
    }
    [STDebug log:[NSString stringWithFormat:@"Could not invert value %@ in item %@ in section %@", self.value, self.key, self.section]];
    return @"ERROR, check log";
}

@end

@interface STConfigurationController : STTableViewController

@end

@implementation STConfigurationController

- (void)reloadStampedData {
    [super reloadStampedData];
    [[STConfiguration sharedInstance] resetValues];
    [self.tableView reloadData];
}

- (void)viewDidAppear:(BOOL)animated {
    [self.tableView reloadData];
}

@end


@interface STConfiguration () <UITableViewDelegate, UITableViewDataSource>

+ (NSString*)sectionForKey:(NSString*)key;

@property (nonatomic, readonly, retain) NSMutableDictionary* objects;
@property (nonatomic, readonly, retain) NSMutableDictionary* sections;
@property (nonatomic, readonly, retain) NSMutableArray* orderedSections;

@end

@implementation STConfiguration

@synthesize objects = objects_;
@synthesize sections = sections_;
@synthesize orderedSections = orderedSections_;

static STConfiguration* _sharedInstance;

+ (void)initialize {
    _sharedInstance = [[STConfiguration alloc] init];
}

+ (STConfiguration *)sharedInstance {
    return _sharedInstance;
}

- (id)init {
    self = [super init];
    if (self) {
        objects_ = [[NSMutableDictionary alloc] init];
        sections_ = [[NSMutableDictionary alloc] init];
        orderedSections_ = [[NSMutableArray alloc] init];
    }
    return self;
}

- (void)dealloc {
    [objects_ release];
    [sections_ release];
    [orderedSections_ release];
    [super dealloc];
}

- (NSInteger)internalVersion {
    return 1;
}

- (id)objectForKey:(NSString*)key {
    STConfigurationItem* item = [self.objects objectForKey:key];
    return item.value;
}

- (NSArray*)keys {
    return [NSArray arrayWithArray:[self.objects allKeys]];
}

- (void)rightButtonClicked:(id)notImportant {
    STDebugDatumViewController* controller = [[[STDebugDatumViewController alloc] initWithString:[self modificationReport]] autorelease];
    [[Util sharedNavigationController] pushViewController:controller animated:YES];
}

- (UIViewController*)controller {
    STTableViewController* controller = [[[STConfigurationController alloc] initWithHeaderHeight:0] autorelease];
    controller.tableView.delegate = [STConfiguration sharedInstance];
    controller.tableView.dataSource = [STConfiguration sharedInstance];
    
    controller.navigationItem.rightBarButtonItem = [[[UIBarButtonItem alloc] initWithTitle:@"Report"
                                                                                     style:UIBarButtonItemStyleDone
                                                                                    target:self 
                                                                                    action:@selector(rightButtonClicked:)] autorelease];
    return controller;
}

- (STConfigurationItem*)itemForSection:(NSString*)section andIndex:(NSInteger)index {
    NSArray* sectionArray = [self.sections objectForKey:section];
    return [self.objects objectForKey:[sectionArray objectAtIndex:index]];  
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section {
    return self.orderedSections.count;
}

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView {
    return 1;
}

- (UITableViewCell*)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
    NSString* section = [self.orderedSections objectAtIndex:indexPath.row];
    
    UITableViewCell* cell = [[[UITableViewCell alloc] initWithStyle:UITableViewCellStyleSubtitle reuseIdentifier:@"TODO"] autorelease];
    cell.textLabel.text = section;
    NSArray* items = [self.sections objectForKey:section];
    NSInteger modified = 0;
    for (NSString* itemName in items) {
        STConfigurationItem* item = [self.objects objectForKey:itemName];
        if (item.modified) {
            modified++;
        }
    }
    if (modified > 0) {
        cell.textLabel.textColor = [UIColor redColor];
    }
    cell.detailTextLabel.text = [NSString stringWithFormat:@"%d items; %d modified", items.count, modified];
    return cell;
}

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
    NSString* section = [self.orderedSections objectAtIndex:indexPath.row];
    
    STTableViewController* controller = [[[STConfigurationSectionController alloc] initWithSection:section] autorelease];
    [[Util sharedNavigationController] pushViewController:controller animated:YES];
}

- (CGFloat)tableView:(UITableView *)tableView heightForRowAtIndexPath:(NSIndexPath *)indexPath {
    return 45;
}

+ (void)addValue:(id)value forKey:(NSString*)key inSection:(NSString*)section {
    STConfigurationItem* item = [[[STConfigurationItem alloc] initWithValue:value key:key andSection:section] autorelease];
    [[STConfiguration sharedInstance] addConfigurationItem:item];
}

- (void)addConfigurationItem:(STConfigurationItem*)item {
    NSMutableArray* section = [self.sections objectForKey:item.section];
    if (!section) {
        section = [[[NSMutableArray alloc] init] autorelease];
        [self.sections setObject:section forKey:item.section];
        [self.orderedSections addObject:item.section];
    }
    [section addObject:item.key];
    [self.objects setObject:item forKey:item.key];
}

+ (NSString*)sectionForKey:(NSString*)key {
    return [[key componentsSeparatedByString:@"."] objectAtIndex:0];
}

+ (void)addFont:(UIFont*)font forKey:(NSString*)key inSection:(NSString*)section {
    STConfigurationStringItem* item = [[[STConfigurationStringItem alloc] initWithValue:font key:key andSection:section] autorelease];
    item.fromString = ^(NSString* string) {
        NSArray* components = [string componentsSeparatedByString:@":"];
        if (components.count == 2) {
            NSNumberFormatter* f = [[[NSNumberFormatter alloc] init] autorelease];
            [f setNumberStyle:NSNumberFormatterDecimalStyle];
            NSNumber* number = [f numberFromString:[components objectAtIndex:1]];
            if (number) {
                return (id)[UIFont fontWithName:[components objectAtIndex:0] size:number.floatValue];
            }
        }
        return (id)nil;
    };
    item.toString = ^(id value) {
        UIFont* theFont = value;
        //NSLog(@"Font:%@,%@",theFont.familyName, theFont.fontName);
        return [NSString stringWithFormat:@"%@:%.1f", theFont.fontName, theFont.pointSize];
    };
    [[STConfiguration sharedInstance] addConfigurationItem:item];
}

+ (void)addString:(NSString*)string forKey:(NSString*)key inSection:(NSString*)section {
    STConfigurationStringItem* stringItem = [[[STConfigurationStringItem alloc] initWithValue:string key:key andSection:section] autorelease];
    [[STConfiguration sharedInstance] addConfigurationItem:stringItem];
}

+ (void)addNumber:(NSNumber*)number forKey:(NSString*)key inSection:(NSString*)section {
    STConfigurationStringItem* item = [[[STConfigurationStringItem alloc] initWithValue:number key:key andSection:section] autorelease];
    item.fromString = ^(NSString* string) {
        NSNumberFormatter* f = [[[NSNumberFormatter alloc] init] autorelease];
        [f setNumberStyle:NSNumberFormatterDecimalStyle];
        return [f numberFromString:string];
    };
    [[STConfiguration sharedInstance] addConfigurationItem:item];
}

+ (void)addColor:(UIColor*)color forKey:(NSString*)key inSection:(NSString*)section {
    id (^fromString)(NSString*) = ^(NSString* string) {
        NSArray* comps = [string componentsSeparatedByString:@", "];
        if (comps.count == 2) {
            NSNumberFormatter* f = [[[NSNumberFormatter alloc] init] autorelease];
            [f setNumberStyle:NSNumberFormatterDecimalStyle];
            NSNumber* alpha = [f numberFromString:[comps objectAtIndex:1]];
            if (alpha && alpha.floatValue >= 0 && alpha.floatValue <= 1) {
                NSString* hexString = [comps objectAtIndex:0];
                CGFloat rgb[3];
                BOOL success = [Util splitHexString:hexString toRGB:rgb];
                if (success) {
                    return (id)[UIColor colorWithRed:rgb[0] green:rgb[1] blue:rgb[2] alpha:alpha.floatValue];
                }
            }
        }
        return (id) nil;
    };
    NSString* (^toString)(id) = ^(id value) {
        UIColor* color2 = value;
        const CGFloat* rgba = CGColorGetComponents( color2.CGColor);
        return [NSString stringWithFormat:@"%@%@%@, %.2f",
                [Util floatToHex:rgba[0]],
                [Util floatToHex:rgba[1]],
                [Util floatToHex:rgba[2]],
                CGColorGetAlpha(color2.CGColor)];
    };
    STConfigurationStringItem* item = [[[STConfigurationStringItem alloc] initWithValue:fromString(toString(color)) key:key andSection:section] autorelease];
    item.fromString = fromString;
    item.toString = toString;
    [[STConfiguration sharedInstance] addConfigurationItem:item];
}

+ (void)addFlag:(BOOL)flag forKey:(NSString*)key inSection:(NSString*)section {
    NSNumber* trueValue = [NSNumber numberWithBool:YES];
    NSNumber* falseValue = [NSNumber numberWithBool:NO];
    NSNumber* cur = flag ? trueValue : falseValue;
    NSDictionary* choices = [NSDictionary dictionaryWithObjectsAndKeys: trueValue, @"True", falseValue, @"False", nil];
    STConfigurationMultipleChoiceItem* item = [[[STConfigurationMultipleChoiceItem alloc] initWithValue:cur
                                                                                                    key:key 
                                                                                                section:section
                                                                                             andChoices:choices] autorelease];
    [[STConfiguration sharedInstance] addConfigurationItem:item];
}

+ (void)addChoices:(NSDictionary*)choices originalKey:(NSString*)originalKey forKey:(NSString*)key inSection:(NSString*)section {
    STConfigurationMultipleChoiceItem* item = [[[STConfigurationMultipleChoiceItem alloc] initWithValue:[choices objectForKey:originalKey]
                                                                                                    key:key 
                                                                                                section:section
                                                                                             andChoices:choices] autorelease];
    [[STConfiguration sharedInstance] addConfigurationItem:item];
}

+ (void)addPoint:(NSValue*)point forKey:(NSString*)key inSection:(NSString*)section {
    id (^fromString)(NSString*) = ^(NSString* string) {
        NSArray* comps = [string componentsSeparatedByString:@","];
        if (comps.count == 2) {
            NSNumber* x = [Util numberFromString:[comps objectAtIndex:0]];
            NSNumber* y = [Util numberFromString:[comps objectAtIndex:1]];
            if (x && y) {
                return (id)[NSValue valueWithCGPoint:CGPointMake(x.floatValue, y.floatValue)];
            }
        }
        return (id) nil;
    };
    NSString* (^toString)(id) = ^(id value) {
        CGPoint point = [value CGPointValue];
        return [NSString stringWithFormat:@"%.1f,%.1f", point.x, point.y];
    };
    STConfigurationStringItem* item = [[[STConfigurationStringItem alloc] initWithValue:point key:key andSection:section] autorelease];
    item.fromString = fromString;
    item.toString = toString;
    [[STConfiguration sharedInstance] addConfigurationItem:item];
}

+ (void)addValue:(id)value forKey:(NSString*)key {
    [self addValue:value forKey:key inSection:[self sectionForKey:key]];
}

+ (void)addFont:(UIFont*)font forKey:(NSString*)key {
    [STConfiguration addFont:font forKey:key inSection:[STConfiguration sectionForKey:key]];
}

+ (void)addString:(NSString*)string forKey:(NSString*)key {
    [STConfiguration addString:string forKey:key inSection:[STConfiguration sectionForKey:key]];
}

+ (void)addNumber:(NSNumber*)number forKey:(NSString*)key {
    [STConfiguration addNumber:number forKey:key inSection:[STConfiguration sectionForKey:key]];
}

+ (void)addColor:(UIColor*)color forKey:(NSString*)key {
    [STConfiguration addColor:color forKey:key inSection:[STConfiguration sectionForKey:key]];
}

+ (void)addFlag:(BOOL)flag forKey:(NSString*)key {
    [STConfiguration addFlag:flag forKey:key inSection:[STConfiguration sectionForKey:key]];
}

+ (void)addChoices:(NSDictionary*)choices originalKey:(NSString*)originalKey forKey:(NSString*)key {
    [self addChoices:choices originalKey:originalKey forKey:key inSection:[self sectionForKey:key]];
}

+ (void)addPoint:(NSValue*)point forKey:(NSString*)key {
    [self addPoint:point forKey:key inSection:[self sectionForKey:key]];
}

+ (id)value:(NSString*)key {
    return [[STConfiguration sharedInstance] objectForKey:key];
}

- (NSArray*)modifiedKeys {
    NSMutableArray* array = [[[NSMutableArray alloc] init] autorelease];
    for (NSString* key in self.keys) {
        STConfigurationItem* item = [self.objects objectForKey:key];
        if (item.modified) {
            [array addObject:item.key];
        }
    }
    return array;
}

- (NSString*)modificationReport {
    NSMutableString* string = [[[NSMutableString alloc] init] autorelease];
    NSString* lastSection = @"";
    for (NSString* key in self.keys) {
        STConfigurationItem* item = [self.objects objectForKey:key];
        if (item.modified) {
            if (![item.section isEqualToString:lastSection]) {
                [string appendFormat:@"\n%@:\n",item.section];
                lastSection = item.section;
            }
            [string appendFormat:@"%@ = %@\n", item.key, item.displayValue];
        }
    }
    return string;
}

- (void)resetValues {
    for (NSString* key in self.modifiedKeys) {
        STConfigurationItem* item = [self.objects objectForKey:key];
        item.value = item.originalValue;
    }
}

- (void)resetValuesInSection:(NSString*)section {
    for (NSString* key in self.modifiedKeys) {
        STConfigurationItem* item = [self.objects objectForKey:key];
        if ([item.section isEqualToString:section]) {
            item.value = item.originalValue;
        }
    }
}

+ (BOOL)flag:(NSString*)key {
    return [[STConfiguration value:key] boolValue];
}

@end

@implementation STConfigurationSectionController

@synthesize section = section_;

- (id)initWithSection:(NSString*)section {
    self = [super initWithHeaderHeight:0];
    if (self) {
        section_ = [section copy];
    }
    return self;
}

- (void)viewDidLoad {
    [super viewDidLoad];
    self.tableView.delegate = self;
    self.tableView.dataSource = self;
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section {
    NSArray* items = [[STConfiguration sharedInstance].sections objectForKey:self.section]; 
    return items.count;
}

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView {
    return 1;
}

- (UITableViewCell*)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
    STConfigurationItem* item = [[STConfiguration sharedInstance] itemForSection:self.section andIndex:indexPath.row];
    return [item tableViewCellWithTableView:tableView];
}

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
    STConfigurationItem* item = [[STConfiguration sharedInstance] itemForSection:self.section andIndex:indexPath.row];
    [item wasSelectedInTableView:tableView atIndexPath:indexPath];
}

- (CGFloat)tableView:(UITableView *)tableView heightForRowAtIndexPath:(NSIndexPath *)indexPath {
    STConfigurationItem* item = [[STConfiguration sharedInstance] itemForSection:self.section andIndex:indexPath.row];
    return [item tableViewCellHeightWithTableView:tableView];
}

- (void)reloadStampedData {
    [super reloadStampedData];
    [[STConfiguration sharedInstance] resetValuesInSection:self.section];
    [self.tableView reloadData];
}

@end
