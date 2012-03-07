//
//  STGalleryItem.h
//  Stamped
//
//  Created by Landon Judkins on 3/6/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>

@protocol STGalleryItem <NSObject>

@property (nonatomic, readonly, retain) NSString* image;
@property (nonatomic, readonly, retain) NSString* caption;
@property (nonatomic, readonly, retain) NSString* link;
@property (nonatomic, readonly, retain) NSString* link_type;
@property (nonatomic, readonly, assign) CGSize size;

@end
