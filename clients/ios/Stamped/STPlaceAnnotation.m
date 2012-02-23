//
//  STPlaceAnnotation.m
//  Stamped
//
//  Created by Andrew Bonventre on 8/16/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "STPlaceAnnotation.h"

#import "Entity.h"
#import "Stamp.h"

const CGFloat kStandardLatLongSpan = 600.0f / 111000.0f;

@implementation STPlaceAnnotation
@synthesize stamp = stamp_;
@synthesize entityObject = entityObject_;

- (id)initWithLatitude:(CLLocationDegrees)latitude
             longitude:(CLLocationDegrees)longitude {
  self = [super init];
  if (self) {
    latitude_ = latitude;
    longitude_ = longitude;
  }
  return self;
}

- (void)dealloc {
  self.stamp = nil;
  self.entityObject = nil;
  [super dealloc];
}

- (CLLocationCoordinate2D)coordinate {
  return CLLocationCoordinate2DMake(latitude_, longitude_);
}

- (NSString*)title {
  if (stamp_)
    return stamp_.entityObject.title;
  
  return entityObject_.title;
}

- (NSString*)subtitle {
  if (stamp_)
    return stamp_.entityObject.subtitle;

  return entityObject_.subtitle;
}

@end
