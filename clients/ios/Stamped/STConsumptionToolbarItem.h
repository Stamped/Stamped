//
//  STConsumptionToolbarItem.h
//  Stamped
//
//  Created by Landon Judkins on 5/7/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>

@interface STConsumptionToolbarItem : NSObject

@property (nonatomic, readwrite, copy) NSString* name;
@property (nonatomic, readwrite, copy) NSString* icon;
@property (nonatomic, readwrite, copy) NSString* backIcon;
@property (nonatomic, readwrite, copy) NSString* value;
@property (nonatomic, readwrite, copy) NSString* type;
@property (nonatomic, readwrite, assign) STConsumptionToolbarItem* parent;
@property (nonatomic, readwrite, copy) NSArray* children;

@end
