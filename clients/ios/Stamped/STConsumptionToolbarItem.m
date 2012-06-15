//
//  STConsumptionToolbarItem.m
//  Stamped
//
//  Created by Landon Judkins on 5/7/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STConsumptionToolbarItem.h"
#import "Util.h"

@implementation STConsumptionToolbarItem

@synthesize name = name_;
@synthesize icon = icon_;
@synthesize value = value_;
@synthesize parent = parent_;
@synthesize children = children_;
@synthesize type = type_;
@synthesize iconValue = _iconValue;

- (id)init {
    self = [super init];
    if (self) {
        children_ = [[NSArray alloc] init];
    }
    return self;
}

- (void)dealloc
{
    [name_ release];
    [icon_ release];
    [value_ release];
    [children_ release];
    [_iconValue release];
    [super dealloc];
}

- (void)setChildren:(NSArray *)children {
    [children_ autorelease];
    children_ = [children copy];
    for (STConsumptionToolbarItem* child in children) {
        child.parent = self;
    }
}

- (UIImage*)guessIcon {
    NSString* category = nil;
    NSString* subcategory = nil;
    NSString* filter = nil;
    
    if (self.type == STConsumptionToolbarItemTypeSection) {
        category = self.iconValue;
    }    
    else if (self.type == STConsumptionToolbarItemTypeSubsection) {
        category = self.parent.iconValue;
        subcategory = self.iconValue;
    }
    else if (self.type == STConsumptionToolbarItemTypeFilter) {
        category = self.parent.parent.iconValue;
        subcategory = self.parent.iconValue;
        filter = self.iconValue;
    }
    return [Util categoryIconForCategory:category subcategory:subcategory filter:filter andSize:STCategoryIconSize15];
}

- (UIImage*)icon {
    if (!icon_) {
        return [self guessIcon];
    }
    else {
        return icon_;
    }
}

- (NSString *)iconValue {
    if (_iconValue) {
        return _iconValue;
    }
    else {
        return value_;
    }
}

@end
