//
//  STGalleryItem.h
//  Stamped
//
//  Created by Landon Judkins on 3/6/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STAction.h"

@protocol STGalleryItem <NSObject>

@property (nonatomic, readonly, retain) NSString* image;
@property (nonatomic, readonly, retain) NSString* caption;
@property (nonatomic, readonly, retain) id<STAction> action;
@property (nonatomic, readonly, assign) NSInteger height;
@property (nonatomic, readonly, assign) NSInteger width;

@end
