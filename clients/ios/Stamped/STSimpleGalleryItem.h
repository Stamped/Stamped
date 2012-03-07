//
//  STSimpleGalleryItem.h
//  Stamped
//
//  Created by Landon Judkins on 3/7/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <RestKit/RestKit.h>
#import "STGalleryItem.h"

@interface STSimpleGalleryItem : NSObject<STGalleryItem>

@property (nonatomic, readwrite, retain) NSString* image;
@property (nonatomic, readwrite, retain) NSString* caption;
@property (nonatomic, readwrite, retain) NSString* link;
@property (nonatomic, readwrite, retain) NSString* link_type;
@property (nonatomic, readwrite, assign) CGSize size;

+ (RKObjectMapping*)mapping;

@end
