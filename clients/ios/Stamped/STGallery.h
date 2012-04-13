//
//  STGallery.h
//  Stamped
//
//  Created by Landon Judkins on 3/8/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STGalleryItem.h"

@protocol STGallery <NSObject>

@property (nonatomic, readonly, copy) NSString* layout;
@property (nonatomic, readonly, retain) NSString* name;
@property (nonatomic, readonly, retain) NSArray<STGalleryItem>* data;

@end
