//
//  ImageToDataTransformer.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/20/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "ImageToDataTransformer.h"

@implementation ImageToDataTransformer

+ (BOOL)allowsReverseTransformation {
  return YES;
}

+ (Class)transformedValueClass {
  return [NSData class];
}

- (id)transformedValue:(id)value {
  // While this may be slower than JPEG, the extra alpha channel is needed for
  // image compositing.
  return UIImagePNGRepresentation(value);
}

- (id)reverseTransformedValue:(id)value {
	return [[[UIImage alloc] initWithData:value] autorelease];
}

@end