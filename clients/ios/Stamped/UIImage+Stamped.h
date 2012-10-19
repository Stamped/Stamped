//
//  UIImage+Stamped.h
//  Stamped
//
//  Created by Landon Judkins on 7/27/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

/*
 
 This category is present solely for iOS 4.3 compatibility.
 
 It extends UIImage to be NSCoding complient, but it doesn't
 take great care with how this workaround affects iOS >= 5.
 Since the HybridCache is used for the model classes and images,
 it relies on NSCoding.
 
 TODO: find a better way of addressing this problem.
 
 2012-08-10
 -Landon
 */

#import <UIKit/UIKit.h>

@interface UIImage (Stamped)

@end
