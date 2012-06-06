//
//  Events.h
//  Stamped
//
//  Created by Devin Doty on 5/31/12.
//
//

#import <UIKit/UIKit.h>

enum EventType {
    
    // twitter
    EventTypeTwitterAuthFinished,
    EventTypeTwitterAuthFailed,
    EventTypeTwitterFriendsFinished,
    
    // facebook
    EventTypeFacebookAuthFinished,
    EventTypeFacebookAuthFailed,
    EventTypeFacebookCameBack,
    
    // signup
    EventTypeSignupFinished,
    
    // friend finding
    EventTypeFriendsFinished,
    
    // user
    EventTypeUserStampsFinished,

	
}; typedef int EventType;

@interface STEvents : NSObject {

}

+ (void)addObserver:(id)observer selector:(SEL)selector event:(EventType)type;
+ (void)addObserver:(id)observer selector:(SEL)selector object:(id)object event:(EventType)type;

+ (void)addObserver:(id)observer selector:(SEL)selector event:(EventType)type identifier:(NSString*)identifier;
+ (void)addObserver:(id)observer selector:(SEL)selector object:(id)object event:(EventType)type identifier:(NSString*)identifier;

+ (void)removeObserver:(id)observer;
+ (void)removeObserver:(id)observer event:(EventType)type;

+ (void)postEvent:(EventType)type;
+ (void)postEvent:(EventType)type object:(id)object;
+ (void)postEvent:(EventType)type identifier:(NSString*)identifier object:(id)object;

@end
