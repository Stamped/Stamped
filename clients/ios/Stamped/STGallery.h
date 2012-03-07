//
//  STGallery.h
//  Stamped
//
//  Created by Landon Judkins on 3/6/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>

@protocol STGalleryItem;

@protocol STGallery <NSObject>

@property (nonatomic, readonly, retain) NSString* name;
@property (nonatomic, readonly, retain) NSArray<STGalleryItem>* data;

@end
