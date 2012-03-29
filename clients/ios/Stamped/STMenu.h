//
//  STMenu.h
//  Stamped
//
//  Created by Landon Judkins on 3/29/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STSubmenu.h"

@protocol STMenu <NSObject>

@property (nonatomic, readonly, retain) NSString* disclaimer;
@property (nonatomic, readonly, retain) NSString* attributionImage;
@property (nonatomic, readonly, retain) NSString* attributionImageLink;
@property (nonatomic, readonly, retain) NSArray<STSubmenu>* menus;

@end
