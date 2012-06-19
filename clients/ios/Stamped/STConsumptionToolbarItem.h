//
//  STConsumptionToolbarItem.h
//  Stamped
//
//  Created by Landon Judkins on 5/7/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <UIKit/UIKit.h>

typedef enum {
    STConsumptionToolbarItemTypeSection,
    STConsumptionToolbarItemTypeSubsection,
    STConsumptionToolbarItemTypeFilter,
} STConsumptionToolbarItemType;

@interface STConsumptionToolbarItem : NSObject

@property (nonatomic, readwrite, copy) NSString* name;
@property (nonatomic, readwrite, retain) UIImage* icon;
@property (nonatomic, readwrite, copy) NSString* value;
@property (nonatomic, readwrite, copy) NSString* iconValue;
@property (nonatomic, readwrite, assign) STConsumptionToolbarItemType type;
@property (nonatomic, readwrite, assign) STConsumptionToolbarItem* parent;
@property (nonatomic, readwrite, copy) NSArray* children;

- (UIImage*)guessIcon;

@end
