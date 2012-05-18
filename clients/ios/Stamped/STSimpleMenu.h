//
//  STSimpleMenu.h
//  Stamped
//
//  Created by Landon Judkins on 3/29/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <RestKit/RestKit.h>
#import "STMenu.h"

@interface STSimpleMenu : NSObject <STMenu, NSCoding>

@property (nonatomic, readwrite, retain) NSString* disclaimer;
@property (nonatomic, readwrite, retain) NSString* attributionImage;
@property (nonatomic, readwrite, retain) NSString* attributionImageLink;
@property (nonatomic, readwrite, retain) NSArray<STSubmenu>* menus;

+ (RKObjectMapping*)mapping;

@end
