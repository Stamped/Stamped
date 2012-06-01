//
//  Events.m
//  Stamped
//
//  Created by Devin Doty on 5/31/12.
//
//

#import "STEvents.h"

#define eventNameFromType(type) [NSString stringWithFormat:@"kStampedNotification-%d",(type)]
#define eventNameFromTypeWithIdentifier(type, identifier) [NSString stringWithFormat:@"kStampedNotification-%d%@",(type), (identifier)]

@implementation STEvents

+ (void)addObserver:(id)observer selector:(SEL)selector event:(EventType)type identifier:(NSString*)identifier {
	[STEvents addObserver:observer selector:selector object:nil event:type identifier:identifier];
}

+ (void)addObserver:(id)observer selector:(SEL)selector event:(EventType)type {
	[STEvents addObserver:observer selector:selector object:nil event:type];
}

+ (void)addObserver:(id)observer selector:(SEL)selector object:(id)object event:(EventType)type identifier:(NSString*)identifier {
	[[NSNotificationCenter defaultCenter] addObserver:observer selector:selector name:eventNameFromTypeWithIdentifier(type, identifier) object:nil];
}

+ (void)addObserver:(id)observer selector:(SEL)selector object:(id)object event:(EventType)type {
	[[NSNotificationCenter defaultCenter] addObserver:observer selector:selector name:eventNameFromType(type) object:nil];
}

+ (void)removeObserver:(id)observer {
	[[NSNotificationCenter defaultCenter] removeObserver:observer];
}

+ (void)removeObserver:(id)observer event:(EventType)type {
	[[NSNotificationCenter defaultCenter] removeObserver:observer name:eventNameFromType(type) object:nil];
}

+ (void)postEvent:(EventType)type {
	[[self class] postEvent:type object:nil];
}

+ (void)postEvent:(EventType)type identifier:(NSString*)identifier object:(id)object {
    
    if (identifier==nil) {
        
        [[self class] postEvent:type object:object];

    } else {
        
        if (![NSThread isMainThread]) {
            
            dispatch_async(dispatch_get_main_queue(), ^{
                [[NSNotificationCenter defaultCenter] postNotificationName:eventNameFromTypeWithIdentifier(type, identifier) object:object]; 
            });
            
        } else {
            
            [[NSNotificationCenter defaultCenter] postNotificationName:eventNameFromTypeWithIdentifier(type, identifier) object:object]; 
            
        }
        
    }
    
}

+ (void)postEvent:(EventType)type object:(id)object {

    if (![NSThread isMainThread]) {
        
        dispatch_async(dispatch_get_main_queue(), ^{
            [[NSNotificationCenter defaultCenter] postNotificationName:eventNameFromType(type) object:object]; 
        });
        
    } else {
        
        [[NSNotificationCenter defaultCenter] postNotificationName:eventNameFromType(type) object:object]; 
        
    }

}

@end
